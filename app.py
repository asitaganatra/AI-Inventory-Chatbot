# app.py (Corrected Version)
import streamlit as st
import time
import sqlite3
import pandas as pd

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser

from datetime import datetime, timedelta

# Simple string output parser
class StrOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        return text

from analytics import (
    get_all_inventory_data,
    add_new_product,
    get_low_stock_alerts,
    get_top_sellers,
    delete_product,
    get_reorder_list,
    get_low_stock_items_for_llm,
    restock_products
)

st.set_page_config(
    page_title="AI-Driven Inventory Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🤖 AI Inventory Assistant (LLM-Powered)")

OWNER_PASSWORD = "owner123"

def clean_text_for_speech(text):
    """Remove markdown formatting from text for speech synthesis while preserving Hindi."""
    import re
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove italic (*text* or _text_)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove links [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    # Remove inline code (`text`)
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Remove only emojis (keep Hindi/Unicode text)
    # This pattern removes emoji ranges but preserves Hindi characters
    text = re.sub(r'[\U0001F300-\U0001F9FF]|[\U0001F600-\U0001F64F]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FA6F]|[\U0001F680-\U0001F6FF]', '', text)
    # Remove markdown symbols but keep punctuation and unicode characters
    text = re.sub(r'[#*_\[\](){}|\\`~^]', ' ', text)
    return text.strip()

# ---- Load API key ----
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key not found. Please create a '.streamlit/secrets.toml' file and add your key.")
    st.stop()

# ---- Initialize LLM ----
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
parser = StrOutputParser()

template = """
You are an AI-powered female inventory assistant with access to real-time inventory, sales, and payment data.
I am here to help you manage your inventory efficiently.

CRITICAL INSTRUCTIONS - KEEP RESPONSES BRIEF:
- Answer in 1-2 sentences by default. Be SHORT and DIRECT.
- Only provide detailed explanations if the user asks for details, more info, or "explain"
- Use female pronouns (I, me, she, her) in responses
- For quick answers: Just state the key fact or number
- For sales/payment queries: Give one main insight with top number
- For product queries: State stock, price, or status in minimal words
- If data is missing, say "I don't have that data" (no suggestions)

Examples of BRIEF responses:
- "Yes, 45 units in stock at Rs. 8,500 each."
- "Total revenue this month: Rs. 2.4 crores."
- "Raj Patel spent Rs. 95,000 on 5 orders."

Inventory & Sales Data:
{inventory_data}

User Question: {user_question}
"""
prompt = PromptTemplate(template=template, input_variables=["inventory_data", "user_question"])

# Modern LangChain pipeline
chain = prompt | llm | parser

# ---- Initialize Chat Session ----
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am your AI-powered Inventory Assistant. I am here to help you manage your inventory efficiently. How can I assist you today?"
    })

if "show_stt_upload" not in st.session_state:
    st.session_state.show_stt_upload = False

# ---- CHAT DISPLAY SECTION ----
st.markdown("### 💬 Chat History")
chat_container = st.container(border=True, height=400)

with chat_container:
    # Display all messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ---- Voice Features: TTS & STT ----
st.markdown("### 🎤 Voice Chat")
col1, col2, col3 = st.columns(3)

with col1:
    voice_lang = st.selectbox("Voice Language", ["English", "Hindi"], key="voice_lang")

with col2:
    # Text-to-Speech: Play last assistant message
    if st.button("🔊 Play Last Reply"):
        try:
            from gtts import gTTS
            import io
            last_assistant = None
            for m in reversed(st.session_state.messages):
                if m.get("role") == "assistant":
                    last_assistant = m.get("content")
                    break
            if last_assistant:
                lang_code = "en" if voice_lang == "English" else "hi"
                tts = gTTS(text=last_assistant, lang=lang_code, slow=False)
                mp3_buffer = io.BytesIO()
                tts.write_to_fp(mp3_buffer)
                mp3_buffer.seek(0)
                st.audio(mp3_buffer.read(), format="audio/mp3")
            else:
                st.info("No assistant reply yet.")
        except Exception as e:
            st.error(f"TTS error: Install gTTS with `pip install gtts`")

with col3:
    # Speech-to-Text: Upload audio file
    if st.button("📁 Upload Audio"):
        st.session_state.show_stt_upload = True

# Speech-to-Text upload
if st.session_state.get("show_stt_upload", False):
    st.markdown("#### Upload WAV/MP3 to Transcribe")
    audio_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a"])
    
    if audio_file:
        try:
            import speech_recognition as sr
            import io
            
            recognizer = sr.Recognizer()
            
            # Load audio file
            if audio_file.type == "audio/mpeg":
                # MP3 file
                st.warning("MP3 support requires ffmpeg. Using WAV is recommended.")
                audio_data = sr.AudioData(audio_file.read(), sample_rate=16000, sample_width=2)
            else:
                # WAV file
                audio_data = sr.AudioData(audio_file.read(), sample_rate=16000, sample_width=2)
            
            lang_code = "en-US" if voice_lang == "English" else "hi-IN"
            transcribed_text = recognizer.recognize_google(audio_data, language=lang_code)
            
            st.success(f"Transcribed: {transcribed_text}")
            
            if st.button("Send Transcribed Text as Message"):
                st.session_state.show_stt_upload = False
                st.session_state.messages.append({"role": "user", "content": transcribed_text})
                st.rerun()
        except Exception as e:
            st.error(f"STT error: {str(e)}. Install with `pip install SpeechRecognition`")

st.markdown("---")

# ---- SIMPLE CHAT WITH MIC (WhatsApp Style) ----
st.markdown("### 💬 Chat")

# Create the chat input and mic button in one row
col_chat, col_mic = st.columns([0.9, 0.1], gap="small")

with col_chat:
    user_input = st.chat_input("Ask me anything about your inventory...", key="chat_input_main")

with col_mic:
    mic_clicked = st.button("🎙️", key="mic_button", help="Click and speak", use_container_width=True)

# If mic button clicked - record and send
mic_transcribed = None
if mic_clicked:
    st.markdown("**🔴 Recording... Speak now!**")
    
    try:
        import speech_recognition as sr
        
        # Check if PyAudio is available (required for microphone access)
        try:
            import pyaudio
        except ImportError:
            st.error("❌ Microphone error: Could not find PyAudio; check installation")
            st.info("💡 Microphone not available in this environment. Use text input instead or upload an audio file above.")
        else:
            recognizer = sr.Recognizer()
            
            # Record from microphone
            try:
                with sr.Microphone() as source:
                    # Record for up to 10 seconds
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
                    
                    # Transcribe to text
                    lang_code = "en-US" if st.session_state.get("voice_lang", "English") == "English" else "hi-IN"
                    transcribed_text = recognizer.recognize_google(audio, language=lang_code)
                    
                    st.success(f"✅ You said: **{transcribed_text}**")
                    
                    # Store for processing below
                    mic_transcribed = transcribed_text
                    
            except sr.UnknownValueError:
                st.error("❌ Couldn't understand. Please speak clearly.")
            except sr.RequestError:
                st.error("❌ Network error. Check your internet.")
                
    except Exception as e:
        st.error(f"❌ Microphone error: {str(e)}")
        st.info("💡 Make sure your microphone is connected and enabled.")

# ---- Chat Input Processing ----
# Use either text input or mic transcribed text
final_user_input = user_input or mic_transcribed

if final_user_input:
    st.session_state.messages.append({"role": "user", "content": final_user_input})
    
    # Re-display all messages in chat container after adding new one
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Process assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if "low stock" in final_user_input.lower() or "restock" in final_user_input.lower():
                    inventory_data = get_low_stock_items_for_llm()
                else:
                    inventory_data = get_all_inventory_data()

                response = chain.invoke({
                    "inventory_data": inventory_data,
                    "user_question": final_user_input
                })
                is_price_query = any(kw in final_user_input.lower() for kw in ['price', 'cost', 'how much', 'kitna'])
                if is_price_query and ('0.0' in response or 'price is 0' in response.lower()):
                    response += "\n\n📝 **Note:** Price not yet set. Ask owner to update in Owner Tools > Edit Product Prices."

                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Convert response to speech and play it
                try:
                    from gtts import gTTS
                    import io
                    
                    # Clean the text for speech (remove markdown formatting)
                    speech_text = clean_text_for_speech(response)
                    
                    lang_code = "en" if st.session_state.get("voice_lang", "English") == "English" else "hi"
                    tts = gTTS(text=speech_text, lang=lang_code, slow=False)
                    mp3_buffer = io.BytesIO()
                    tts.write_to_fp(mp3_buffer)
                    mp3_buffer.seek(0)
                    
                    st.audio(mp3_buffer.read(), format="audio/mp3", autoplay=True)
                    
                except Exception as audio_error:
                    st.warning(f"⚠️ Could not generate audio: {str(audio_error)}. Text response is available.")
                
                # Re-display chat with new assistant response
                with chat_container:
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                # Re-display chat with error message
                with chat_container:
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])


# ---- SIDEBAR: Dashboard (Always Visible) + Owner Tools ----
with st.sidebar:
    st.header("📊 Inventory Dashboard")

    st.subheader("Products Nearing Restock Point")
    low_stock_df = get_low_stock_alerts()
    if not low_stock_df.empty:
        st.dataframe(low_stock_df, hide_index=True, use_container_width=True)
    else:
        st.success("All products are well-stocked!")

    st.markdown("---")

    st.subheader("Top Selling Products (Last 30 Days)")
    top_sellers_df = get_top_sellers()
    if not top_sellers_df.empty:
        st.bar_chart(
            data=top_sellers_df,
            x="product_name",
            y="total_sales"
        )
    else:
        st.info("Not enough sales data yet to show top sellers.")

    st.markdown("---")
    st.header("🔑 Owner Access")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.form(key="login_form"):
            password_input = st.text_input("Enter owner password", type="password")
            login_button = st.form_submit_button("Log In")

            if login_button:
                if password_input == OWNER_PASSWORD:
                    st.session_state.logged_in = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Incorrect password.")
    
    if st.session_state.logged_in:
        if st.button("Log Out", key="logout_button"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.markdown("---")
        
        with st.expander("🔐 Owner Tools"):
            # ---- Add Product ----
            st.subheader("Add a New Product")

            if 'add_status_message' not in st.session_state:
                st.session_state.add_status_message = (None, None)

            msg_type, msg_text = st.session_state.add_status_message
            if msg_type == "success":
                st.success(msg_text)
            elif msg_type == "error":
                st.error(msg_text)
            elif msg_type == "warning":
                st.warning(msg_text)

            with st.form(key='add_product_form'):
                new_product_id = st.text_input("Product ID (e.g., PROD006)")
                new_product_name = st.text_input("Product Name")
                new_category = st.text_input("Category")
                new_stock = st.number_input("Initial Stock", min_value=0, value=100)
                new_reorder_point = st.number_input("Reorder Point", min_value=0, value=20)

                try:
                    conn = sqlite3.connect('inventory.db')
                    suppliers_df = pd.read_sql_query("SELECT supplier_id, supplier_name FROM suppliers", conn)
                    supplier_options = {row['supplier_name']: row['supplier_id'] for _, row in suppliers_df.iterrows()}
                    conn.close()
                except Exception:
                    supplier_options = {}

                selected_supplier_name = st.selectbox("Select a Supplier", list(supplier_options.keys()))
                new_supplier_id = supplier_options.get(selected_supplier_name)

                submitted = st.form_submit_button("Add Product")

            if submitted:
                if new_product_id and new_product_name:
                    success = add_new_product(
                        new_product_id.upper(),
                        new_product_name,
                        new_category,
                        new_stock,
                        new_reorder_point,
                        new_supplier_id
                    )
                    if success:
                        st.session_state.add_status_message = (
                            "success", f"Successfully added: {new_product_name}"
                        )
                    else:
                        st.session_state.add_status_message = (
                            "error", f"Failed to add product. ID '{new_product_id}' might already exist."
                        )
                else:
                    st.session_state.add_status_message = (
                        "warning", "Product ID and Name are required."
                    )
                st.rerun()

            # ---- Edit Product Prices ----
            st.markdown("---")
            st.subheader("💰 Edit Product Prices")
            with st.form(key='edit_price_form'):
                try:
                    conn = sqlite3.connect('inventory.db')
                    df_products = pd.read_sql_query("SELECT product_id, product_name, unit_price, current_stock FROM products ORDER BY product_id", conn)
                    conn.close()
                    product_list = list(df_products['product_id'])
                except Exception:
                    product_list = []
                    df_products = pd.DataFrame()
                if product_list:
                    selected_product = st.selectbox("Select a product to edit price", product_list, key="price_edit_select")
                    current_row = df_products[df_products['product_id'] == selected_product]
                    if not current_row.empty:
                        current_price = float(current_row.iloc[0]['unit_price'] or 0.0)
                        current_stock = int(current_row.iloc[0]['current_stock'] or 0)
                        product_name = current_row.iloc[0]['product_name']
                        st.write(f"**Product:** {product_name} | **Stock:** {current_stock} | **Price:** ${current_price:.2f}")
                        new_price = st.number_input("New Unit Price ($)", min_value=0.0, value=current_price, step=0.01, key="new_price_input")
                        if st.form_submit_button("Update Price"):
                            conn = sqlite3.connect('inventory.db')
                            new_total = new_price * current_stock
                            conn.execute("UPDATE products SET unit_price=?, total_value=?, updated_date=? WHERE product_id=?", (new_price, new_total, pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'), selected_product))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ {product_name}: ${new_price:.2f}/unit (Total: ${new_total:.2f})")
                            st.rerun()
                else:
                    st.warning("No products found.")
            # ---- Delete Product ----
            st.markdown("---")
            st.subheader("Delete a Product")

            with st.form(key='delete_product_form'):
                try:
                    conn = sqlite3.connect('inventory.db')
                    df_products = pd.read_sql_query("SELECT product_id FROM products", conn)
                    conn.close()
                    product_list = list(df_products['product_id'])
                except Exception:
                    product_list = []

                if product_list:
                    product_to_delete = st.selectbox("Select a product to delete", product_list)
                    delete_button = st.form_submit_button("Delete Product")

                    if delete_button:
                        if delete_product(product_to_delete):
                            st.success(f"Successfully deleted: {product_to_delete}")
                            st.rerun()
                        else:
                            st.error("Could not delete product.")
                else:
                    st.warning("No products to delete.")

            # ---- Restock Management ----
            st.markdown("---")
            st.subheader("✍️ Restock & Order Workflow")

            # Initialize restock workflow state
            if 'restock_workflow_stage' not in st.session_state:
                st.session_state.restock_workflow_stage = "initial"  # initial -> letter_generated -> sent -> bill_generated -> paid -> completed
            if 'generated_letter' not in st.session_state:
                st.session_state.generated_letter = None
            if 'bill_amount' not in st.session_state:
                st.session_state.bill_amount = 0
            if 'restock_data' not in st.session_state:
                st.session_state.restock_data = None

            reorder_df = get_reorder_list()

            if not reorder_df.empty:
                st.write("Low Stock Items:")
                st.info("Edit the 'Restock Quantity' column to place an order.")

                restock_quantities = st.data_editor(
                    reorder_df,
                    column_config={
                        "product_id": st.column_config.TextColumn("Product ID", disabled=True),
                        "current_stock": st.column_config.NumberColumn("Current Stock", disabled=True),
                        "reorder_point": st.column_config.NumberColumn("Reorder Point", disabled=True),
                        "product_name": st.column_config.TextColumn("Product", disabled=True),
                        "restock_quantity": st.column_config.NumberColumn("Restock Quantity", min_value=1, step=1, default=10),
                        "supplier_name": st.column_config.TextColumn("Supplier", disabled=True),
                        "contact_email": st.column_config.TextColumn("Email", disabled=True)
                    },
                    hide_index=True,
                    num_rows="fixed"
                )

                # ---- STAGE 1: Generate Letter ----
                if st.session_state.restock_workflow_stage == "initial":
                    if st.button("📝 Step 1: Generate Letter"):
                        restock_dict = dict(zip(reorder_df['product_id'], restock_quantities['restock_quantity']))
                        
                        # Create letter
                        reorder_text = "═" * 50 + "\n"
                        reorder_text += "📬 PURCHASE ORDER LETTER\n"
                        reorder_text += "═" * 50 + "\n\n"
                        reorder_text += f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n"
                        reorder_text += "To the Supplier,\n\n"
                        reorder_text += "Please restock the following items:\n\n"
                        
                        total_cost = 0
                        for _, row in restock_quantities.iterrows():
                            qty = int(row['restock_quantity'])
                            unit_price = 50  # Default unit price (can be customized)
                            cost = qty * unit_price
                            total_cost += cost
                            reorder_text += f"• {row['product_name']} (ID: {row['product_id']})\n"
                            reorder_text += f"  Quantity: {qty} units\n"
                            reorder_text += f"  Estimated Cost: ${cost}\n\n"
                        
                        reorder_text += "═" * 50 + "\n"
                        reorder_text += f"Total Estimated Cost: ${total_cost}\n"
                        reorder_text += "═" * 50 + "\n\n"
                        reorder_text += "Please confirm receipt and delivery timeline.\n"
                        reorder_text += "Thank you,\nStore Owner"
                        
                        st.session_state.generated_letter = reorder_text
                        st.session_state.bill_amount = total_cost
                        st.session_state.restock_data = restock_dict
                        st.session_state.restock_workflow_stage = "letter_generated"
                        st.rerun()

                # ---- STAGE 2: Finalize & Display Letter ----
                if st.session_state.restock_workflow_stage == "letter_generated":
                    st.markdown("### 📝 Your Purchase Order Letter")
                    st.text_area("Letter Preview:", value=st.session_state.generated_letter, height=300, disabled=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Finalize & Send Letter"):
                            st.session_state.restock_workflow_stage = "sent"
                            st.success("✅ Letter sent to supplier!")
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel & Edit"):
                            st.session_state.restock_workflow_stage = "initial"
                            st.session_state.generated_letter = None
                            st.rerun()

                # ---- STAGE 3: Display Bill ----
                if st.session_state.restock_workflow_stage == "sent":
                    st.markdown("---")
                    st.markdown("### 💰 Invoice / Bill")
                    
                    bill_html = f"""
                    <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 8px; background-color: #f9f9f9;">
                        <h3 style="text-align: center; color: #2c3e50;">📋 PURCHASE INVOICE</h3>
                        <hr/>
                        <p><strong>Invoice Date:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <p><strong>Status:</strong> <span style="color: #FF9800;">🟠 PENDING PAYMENT</span></p>
                        <hr/>
                        <h4>Items Ordered:</h4>
                        <ul>
                    """
                    
                    for _, row in restock_quantities.iterrows():
                        qty = int(row['restock_quantity'])
                        unit_price = 50
                        cost = qty * unit_price
                        bill_html += f"<li>{row['product_name']} - {qty} units @ ${unit_price}/unit = ${cost}</li>"
                    
                    bill_html += f"""
                        </ul>
                        <hr/>
                        <h3 style="text-align: right; color: #2c3e50;">
                            Total Amount Due: <span style="color: #4CAF50; font-size: 24px;">${st.session_state.bill_amount}</span>
                        </h3>
                    </div>
                    """
                    st.markdown(bill_html, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    if st.button("💳 Proceed to Payment"):
                        st.session_state.restock_workflow_stage = "bill_generated"
                        st.rerun()

                # ---- STAGE 4: Payment Gateway ----
                if st.session_state.restock_workflow_stage == "bill_generated":
                    st.markdown("### 💳 Payment Gateway")
                    st.warning(f"⚠️ Payment Due: **${st.session_state.bill_amount}**")
                    
                    payment_method = st.radio("Select Payment Method:", ["Credit Card", "Debit Card", "Bank Transfer", "PayPal"])
                    
                    if payment_method == "Credit Card":
                        st.text_input("Card Number", placeholder="1234 5678 9012 3456", type="password")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.text_input("Expiry Date", placeholder="MM/YY")
                        with col2:
                            st.text_input("CVV", placeholder="123", type="password")
                    elif payment_method == "Debit Card":
                        st.text_input("Card Number", placeholder="1234 5678 9012 3456", type="password")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.text_input("Expiry Date", placeholder="MM/YY")
                        with col2:
                            st.text_input("CVV", placeholder="123", type="password")
                    elif payment_method == "Bank Transfer":
                        st.info("Bank Account: XXX-XXXX-XXXX\nBSB: 000-000")
                    elif payment_method == "PayPal":
                        st.text_input("PayPal Email", placeholder="example@paypal.com")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Pay ${st.session_state.bill_amount}"):
                            st.session_state.restock_workflow_stage = "paid"
                            st.success(f"✅ Payment of ${st.session_state.bill_amount} processed successfully!")
                            st.balloons()
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Back"):
                            st.session_state.restock_workflow_stage = "sent"
                            st.rerun()

                # ---- STAGE 5: Confirm Restock ----
                if st.session_state.restock_workflow_stage == "paid":
                    st.markdown("---")
                    st.success("💚 Payment Completed! Now Restocking Products...")
                    st.markdown("### ✅ Final Step: Restock Products")
                    
                    st.info("""
                    Your payment has been confirmed. Click the button below to complete the restock process.
                    All products will be added to your inventory.
                    """)
                    
                    if st.button("🔄 Complete Restock Process"):
                        if st.session_state.restock_data and restock_products(st.session_state.restock_data):
                            st.success("✅ All products have been restocked successfully!")
                            st.markdown("### 📊 Restock Summary:")
                            
                            summary_text = "**Restocked Items:**\n\n"
                            for _, row in restock_quantities.iterrows():
                                qty = int(row['restock_quantity'])
                                summary_text += f"• {row['product_name']}: +{qty} units\n"
                            
                            st.markdown(summary_text)
                            
                            # Download receipt
                            receipt = f"""
PURCHASE RECEIPT
{'='*50}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
Amount Paid: ${st.session_state.bill_amount}
Status: COMPLETED ✅

ITEMS RESTOCKED:
{summary_text.replace('**', '').replace('_', '')}

{'='*50}
Thank you for your purchase!
                            """
                            
                            st.download_button(
                                label="📥 Download Receipt",
                                data=receipt,
                                file_name=f"restock_receipt_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                            
                            # Reset workflow
                            if st.button("🔄 Start New Restock Order"):
                                st.session_state.restock_workflow_stage = "initial"
                                st.session_state.generated_letter = None
                                st.session_state.bill_amount = 0
                                st.session_state.restock_data = None
                                st.rerun()
                        else:
                            st.error("Failed to restock products. Please try again.")
            else:
                st.info("No items need to be restocked.")

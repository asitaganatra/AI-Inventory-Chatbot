import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Import our existing inventory management functions
from inventory_utils import (
    get_inventory_status,
    check_low_stock_items,
    get_product_details
)

# --- 1. Knowledge Base ---
# This dictionary defines what our chatbot can understand.
# The 'intent' is the key, and the 'patterns' are example phrases.
knowledge_base = {
    "get_inventory_status": {
        "patterns": ["show all inventory", "what's in stock", "inventory status", "list all products"],
        "response_template": "Here is the full inventory status:"
    },
    "check_low_stock": {
        "patterns": ["low stock items", "what needs restocking", "show me low inventory", "are we running out of anything"],
        "response_template": "Here are the items that are currently low on stock:"
    },
    "get_product_details": {
        "patterns": ["how many {} do we have", "what is the stock level for {}", "details for {}", "tell me about {}"],
        # The {} is a placeholder for a product name (an 'entity')
    },
    "greet": {
        "patterns": ["hello", "hi", "hey", "good morning"],
        "response_template": "Hello! How can I help you with your inventory today?"
    },
    "goodbye": {
        "patterns": ["bye", "goodbye", "see you later", "thanks bye"],
        "response_template": "Goodbye! Have a great day."
    },
}

# --- 2. NLP Processing Core ---

# Combine all patterns into a single list for the vectorizer
all_patterns = []
for intent, data in knowledge_base.items():
    if "patterns" in data:
        all_patterns.extend(data["patterns"])

# Initialize and train the TF-IDF Vectorizer
# TF-IDF stands for Term Frequency-Inverse Document Frequency. It's a way to
# represent words with numbers, giving more importance to words that are
# unique to a specific pattern.
vectorizer = TfidfVectorizer().fit(all_patterns)

def get_intent(user_query):
    """
    This function uses cosine similarity to find the best matching intent
    for a user's query.
    """
    # Convert the user query into a TF-IDF vector
    query_vector = vectorizer.transform([user_query])

    # Calculate similarity scores between the user query and all known patterns
    max_similarity = 0
    best_intent = "unknown"

    for intent, data in knowledge_base.items():
        if "patterns" in data:
            # Convert all patterns for this intent into vectors
            patterns_vector = vectorizer.transform(data["patterns"])
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, patterns_vector)
            # Find the highest similarity score for this intent
            current_max_sim = np.max(similarities)
            
            if current_max_sim > max_similarity:
                max_similarity = current_max_sim
                best_intent = intent
    
    # We set a confidence threshold. If the best match is too weak,
    # we classify it as unknown. This prevents weird matches.
    if max_similarity > 0.3:
        return best_intent
    else:
        return "unknown"

def extract_product_name(user_query):
    """
    A simple function to find a product name within the user's query.
    This is a basic form of Named Entity Recognition (NER).
    """
    inventory_df = get_inventory_status()
    product_names = inventory_df['ProductName'].str.lower().tolist()
    
    for word in user_query.lower().split():
        # A more robust check for multi-word product names
        for product in product_names:
            if product in user_query.lower():
                # We need to return the correctly cased product name
                original_case_product = inventory_df[inventory_df['ProductName'].str.lower() == product]['ProductName'].iloc[0]
                return original_case_product
    return None

def get_bot_response(user_query):
    """
    The main function that orchestrates the chatbot's response generation.
    """
    intent = get_intent(user_query)
    
    if intent == "greet":
        return knowledge_base["greet"]["response_template"]
        
    elif intent == "goodbye":
        return knowledge_base["goodbye"]["response_template"]
        
    elif intent == "get_inventory_status":
        inventory_df = get_inventory_status()
        # To avoid printing a huge table in the chat, we'll summarize.
        # The full table is already on the dashboard.
        return f"There are {len(inventory_df)} products in stock. You can see the full list on the 'Full Inventory' tab."

    elif intent == "check_low_stock":
        low_stock_df = check_low_stock_items()
        if low_stock_df.empty:
            return "👍 Great news! No items are currently low on stock."
        else:
            items = ", ".join(low_stock_df['ProductName'].tolist())
            return f"🚨 The following items are running low: {items}. Check the 'Low Stock Items' tab for details."

    elif intent == "get_product_details":
        product_name = extract_product_name(user_query)
        if product_name:
            details = get_product_details(product_name)
            if details:
                response = (
                    f"Here are the details for **{details['ProductName']}**:\n"
                    f"- **Stock Level:** {details['StockLevel']} units\n"
                    f"- **Price:** ${details['Price']:.2f}\n"
                    f"- **Category:** {details['Category']}\n"
                    f"- **Reorder Level:** {details['ReorderLevel']} units"
                )
                if details['StockLevel'] <= details['ReorderLevel']:
                    response += "\n- **Status:** ⚠️ This item is low on stock."
                return response
            else:
                return f"Sorry, I couldn't find any details for '{product_name}'."
        else:
            return "I can help with that, but which product are you asking about?"

    else: # This is the "unknown" case
        return "I'm sorry, I didn't understand that. You can ask me to 'show all inventory', 'check low stock items', or ask about a specific product like 'how many organic apples do we have?'"
    
# chatbot_nlp.py
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

def process_user_query(text):
    if nlp is None:
        return "error", {}

    doc = nlp(text.lower())
    intent = "unknown"
    entities = {}

    if "stock" in text.lower() or "inventory" in text.lower() or "how many" in text.lower():
        intent = "get_stock_status"
    elif "low stock" in text.lower() or "restock" in text.lower() or "reorder" in text.lower() or "alert" in text.lower():
        intent = "get_low_stock_alerts"
    elif "top" in text.lower() or "best seller" in text.lower():
        intent = "get_top_sellers"
    elif "hello" in text.lower() or "hi" in text.lower():
        intent = "greet"

    for token in doc:
        if token.pos_ == "NOUN" and token.text not in ["stock", "inventory", "sales", "demand", "reorder", "products", "items"]:
            entities['product_name'] = token.text
            break
    
    return intent, entities
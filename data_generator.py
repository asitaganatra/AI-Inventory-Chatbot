# data_generator.py (Updated to be truly dynamic)
import sqlite3
import pandas as pd
import time
import random
from datetime import datetime
from faker import Faker


fake = Faker()
DB_NAME = 'inventory.db'

def get_db_connection():
    return sqlite3.connect(DB_NAME)

# NOTE: We no longer get products here
# products_df = pd.read_sql_query("SELECT product_id, current_stock FROM products", get_db_connection())

def generate_and_add_sale():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # --- NEW CODE: Get the product list on every transaction ---
        products_df = pd.read_sql_query("SELECT product_id, current_stock FROM products", conn)
        
        if products_df.empty:
            print("No products found. Exiting generator.")
            return

        product_to_sell = products_df.sample(n=1)
        product_id = product_to_sell['product_id'].iloc[0]
        quantity_sold = random.randint(1, 5)

        new_stock = int(product_to_sell['current_stock'].iloc[0]) - quantity_sold
        if new_stock >= 0:
            cursor.execute(
                "UPDATE products SET current_stock = ? WHERE product_id = ?",
                (new_stock, product_id)
            )
            sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO sales_history (product_id, quantity_sold, sale_date) VALUES (?, ?, ?)",
                (product_id, quantity_sold, sale_date)
            )
            conn.commit()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sale added for {product_id}. {quantity_sold} units sold. New stock: {new_stock}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Not enough stock for {product_id}. Skipping sale.")

if __name__ == "__main__":
    print("Starting dynamic data generator. Open another terminal for the chatbot.")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            generate_and_add_sale()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Data generation stopped.")
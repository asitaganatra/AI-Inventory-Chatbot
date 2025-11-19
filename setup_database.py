# setup_database.py (Enhanced Version with Real-Life Attributes)
import sqlite3
import pandas as pd
from datetime import datetime

def setup_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # --- Create the enhanced products table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            current_stock INTEGER,
            reorder_point INTEGER,
            supplier_id TEXT,
            unit_price REAL DEFAULT 0.0,
            total_value REAL DEFAULT 0.0,
            restock_date TEXT,
            restock_time TEXT,
            last_restock_quantity INTEGER DEFAULT 0,
            total_restocks INTEGER DEFAULT 0,
            manufacture_date TEXT,
            expiry_date TEXT,
            warehouse_location TEXT,
            sku_code TEXT UNIQUE,
            created_date TEXT,
            updated_date TEXT
        )
    ''')
    
    # --- Create the enhanced sales history table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_history (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            quantity_sold INTEGER,
            unit_price REAL,
            total_amount REAL,
            sale_date TEXT,
            sale_time TEXT,
            customer_name TEXT,
            payment_method TEXT,
            notes TEXT,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    # Create the suppliers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id TEXT PRIMARY KEY,
            supplier_name TEXT,
            contact_email TEXT,
            phone_number TEXT,
            address TEXT,
            city TEXT,
            country TEXT,
            payment_terms TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database `inventory.db` set up with enhanced schema successfully.")

if __name__ == '__main__':
    setup_db()
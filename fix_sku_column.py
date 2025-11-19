import sqlite3

def fix_sku_column():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    try:
        # Drop and recreate the table with sku_code as regular column (non-unique)
        cursor.execute("""
            CREATE TABLE products_new (
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
                sku_code TEXT,
                created_date TEXT,
                updated_date TEXT
            )
        """)
        
        # Copy data from old table
        cursor.execute("""
            INSERT INTO products_new 
            SELECT * FROM products
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE products")
        cursor.execute("ALTER TABLE products_new RENAME TO products")
        
        conn.commit()
        print("✅ Fixed SKU column - changed from UNIQUE to regular column")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    fix_sku_column()

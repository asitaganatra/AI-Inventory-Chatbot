import sqlite3

# PROD001 to add back
product = ("PROD001", "Office Chair", "Furniture", 15, 5, "SUP003")

try:
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO products (product_id, product_name, category, current_stock, reorder_point, supplier_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, product)
        conn.commit()
        print(f"✅ Successfully added: {product[1]} ({product[0]})")
    except sqlite3.IntegrityError:
        print(f"⚠️  PROD001 already exists in database")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

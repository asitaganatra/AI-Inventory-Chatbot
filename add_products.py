import sqlite3
import pandas as pd

# Products to add
products = [
    ("PROD010", "Noise Cancelling Headset", "Electronics", 75, 35, "SUP001"),
    ("PROD011", "External SSD 1TB", "Electronics", 55, 25, "SUP005"),
    ("PROD012", "USB-C Hub (7-in-1)", "Electronics", 110, 40, "SUP005"),
    ("PROD013", "Printer Ink Cartridge", "Supplies", 250, 100, "SUP006"),
    ("PROD014", "A4 Printer Paper (Case)", "Supplies", 300, 150, "SUP006"),
    ("PROD015", "File Cabinet (4-Drawer)", "Furniture", 8, 3, "SUP003"),
    ("PROD016", "Whiteboard (Large)", "Supplies", 12, 5, "SUP004"),
    ("PROD017", "Dry Erase Markers (Box)", "Supplies", 180, 70, "SUP006"),
    ("PROD018", "Desk Organizer Tray", "Supplies", 150, 60, "SUP004"),
    ("PROD019", "Server Rack 42U", "Furniture", 3, 1, "SUP003"),
    ("PROD020", "Network Switch (24 Port)", "Electronics", 20, 10, "SUP005"),
]

try:
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    added = 0
    failed = 0
    
    for product in products:
        try:
            cursor.execute("""
                INSERT INTO products (product_id, product_name, category, current_stock, reorder_point, supplier_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, product)
            added += 1
            print(f"✅ Added: {product[1]} ({product[0]})")
        except sqlite3.IntegrityError:
            failed += 1
            print(f"⚠️  Already exists: {product[0]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"Summary: {added} added, {failed} already existed")
    print(f"{'='*50}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

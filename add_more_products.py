import sqlite3

# Products to add
products = [
    ("PROD021", "HDMI Cable (10ft)", "Electronics", 220, 80, "SUP005"),
    ("PROD022", "Power Strip (Surge Protect)", "Electronics", 190, 75, "SUP004"),
    ("PROD023", "Label Maker", "Electronics", 45, 20, "SUP001"),
    ("PROD024", "AA Batteries (Pack of 12)", "Supplies", 400, 200, "SUP006"),
    ("PROD025", "Security Camera (Indoor)", "Electronics", 35, 15, "SUP001"),
    ("PROD026", "Visitor Sign-In Book", "Supplies", 80, 40, "SUP006"),
    ("PROD027", "Shredder (Cross-Cut)", "Electronics", 18, 8, "SUP004"),
    ("PROD028", "Monitor 27\" 4K", "Electronics", 30, 10, "SUP001"),
    ("PROD029", "Laptop (Business Grade)", "Electronics", 10, 5, "SUP005"),
    ("PROD030", "Desk Pad/Mat", "Supplies", 95, 40, "SUP004"),
    ("PROD031", "Stapler (Heavy Duty)", "Supplies", 70, 30, "SUP006"),
    ("PROD032", "Thermal Printer Rolls", "Supplies", 160, 60, "SUP006"),
    ("PROD033", "VoIP Phone Handset", "Electronics", 25, 10, "SUP001"),
    ("PROD034", "Projector (Meeting Room)", "Electronics", 5, 2, "SUP005"),
    ("PROD035", "Wireless Charger Pad", "Electronics", 65, 30, "SUP002"),
    ("PROD036", "Ergonomic Footrest", "Furniture", 40, 15, "SUP003"),
    ("PROD037", "Bookshelf (Open)", "Furniture", 7, 3, "SUP003"),
    ("PROD038", "Ethernet Cable (Cat6 50ft)", "Electronics", 130, 50, "SUP002"),
    ("PROD039", "USB Flash Drive (128GB)", "Electronics", 150, 75, "SUP002"),
    ("PROD040", "Mouse Pad (Gel Wrist Rest)", "Supplies", 115, 50, "SUP004"),
    ("PROD041", "First Aid Kit (Office Size)", "Supplies", 22, 10, "SUP006"),
    ("PROD042", "Surge Protector Rack Mount", "Electronics", 15, 5, "SUP005"),
    ("PROD043", "Headphone Splitter", "Electronics", 200, 80, "SUP002"),
    ("PROD044", "Cable Management Sleeves", "Supplies", 180, 70, "SUP004"),
    ("PROD045", "Desk Lamp LED (Dimmable)", "Electronics", 60, 25, "SUP002"),
    ("PROD046", "Privacy Screen Filter 27\"", "Electronics", 30, 12, "SUP001"),
    ("PROD047", "Keyboard Cleaning Gel", "Supplies", 90, 40, "SUP006"),
    ("PROD048", "Mobile Workstation Cart", "Furniture", 4, 2, "SUP003"),
    ("PROD049", "DisplayPort Cable", "Electronics", 140, 60, "SUP002"),
    ("PROD050", "Hand Sanitizer (Gallon)", "Supplies", 110, 50, "SUP006"),
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

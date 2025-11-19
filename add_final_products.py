import sqlite3

# 50 More Products to add
products = [
    ("PROD051", "Wireless Mouse", "Electronics", 200, 80, "SUP001"),
    ("PROD052", "USB-A to USB-C Cable", "Electronics", 150, 60, "SUP002"),
    ("PROD053", "Desk Chair (Ergonomic)", "Furniture", 5, 2, "SUP003"),
    ("PROD054", "File Folder (Hanging)", "Supplies", 500, 200, "SUP004"),
    ("PROD055", "Monitor Arm Stand", "Furniture", 25, 10, "SUP003"),
    ("PROD056", "Mechanical Keyboard", "Electronics", 40, 15, "SUP001"),
    ("PROD057", "Webcam 1080p HD", "Electronics", 35, 12, "SUP002"),
    ("PROD058", "Notebook (A4, 100 pages)", "Supplies", 300, 120, "SUP004"),
    ("PROD059", "Ballpoint Pen (Box of 50)", "Supplies", 250, 100, "SUP006"),
    ("PROD060", "Desk Organizer (5-Drawer)", "Furniture", 20, 8, "SUP003"),
    ("PROD061", "External Hard Drive 2TB", "Electronics", 45, 18, "SUP005"),
    ("PROD062", "Laser Pointer", "Supplies", 100, 40, "SUP004"),
    ("PROD063", "Office Chair Mat (PVC)", "Supplies", 30, 12, "SUP004"),
    ("PROD064", "Portable Speaker Bluetooth", "Electronics", 55, 20, "SUP001"),
    ("PROD065", "Desk Lamp (Task Light)", "Electronics", 70, 25, "SUP002"),
    ("PROD066", "Phone Stand", "Supplies", 120, 50, "SUP004"),
    ("PROD067", "Bookmark (Metal, 100pcs)", "Supplies", 400, 150, "SUP006"),
    ("PROD068", "Laptop Stand", "Furniture", 35, 14, "SUP003"),
    ("PROD069", "USB Hub 7-Port", "Electronics", 60, 22, "SUP005"),
    ("PROD070", "Document Scanner", "Electronics", 15, 5, "SUP001"),
    ("PROD071", "Whiteboard Pen (Set of 10)", "Supplies", 200, 80, "SUP006"),
    ("PROD072", "Floor Mat (Rubber)", "Supplies", 25, 10, "SUP004"),
    ("PROD073", "Fax Machine", "Electronics", 8, 3, "SUP005"),
    ("PROD074", "Paper Shredder (Desktop)", "Electronics", 20, 8, "SUP001"),
    ("PROD075", "Pen Holder (Ceramic)", "Supplies", 150, 60, "SUP004"),
    ("PROD076", "Microphone USB", "Electronics", 50, 18, "SUP002"),
    ("PROD077", "Adhesive Tape (Heavy Duty)", "Supplies", 300, 120, "SUP006"),
    ("PROD078", "Clipboard (Wooden)", "Supplies", 80, 30, "SUP004"),
    ("PROD079", "Portable Projector", "Electronics", 12, 4, "SUP005"),
    ("PROD080", "Desk Blotter Pad", "Supplies", 100, 40, "SUP004"),
    ("PROD081", "Wireless Keyboard", "Electronics", 85, 32, "SUP001"),
    ("PROD082", "Document Holder", "Supplies", 110, 45, "SUP004"),
    ("PROD083", "Power Bank 10000mAh", "Electronics", 75, 28, "SUP002"),
    ("PROD084", "Desk Calendar", "Supplies", 200, 80, "SUP006"),
    ("PROD085", "Illuminated Magnifier", "Electronics", 30, 12, "SUP001"),
    ("PROD086", "Index Cards (1000pcs)", "Supplies", 350, 140, "SUP006"),
    ("PROD087", "Desk Hutch", "Furniture", 12, 5, "SUP003"),
    ("PROD088", "Surge Protector Power Strip", "Electronics", 100, 40, "SUP005"),
    ("PROD089", "Label Roll", "Supplies", 250, 100, "SUP006"),
    ("PROD090", "Monitor Light Bar", "Electronics", 45, 16, "SUP002"),
    ("PROD091", "Desk Pad (Non-Slip)", "Supplies", 120, 48, "SUP004"),
    ("PROD092", "Cordless Phone", "Electronics", 25, 10, "SUP001"),
    ("PROD093", "Pencil Eraser (Box of 24)", "Supplies", 200, 80, "SUP006"),
    ("PROD094", "Adjustable Monitor Stand", "Furniture", 40, 15, "SUP003"),
    ("PROD095", "Cable Organizer Clips", "Supplies", 180, 70, "SUP004"),
    ("PROD096", "Ring Light", "Electronics", 55, 20, "SUP002"),
    ("PROD097", "Envelopes (Pack of 100)", "Supplies", 300, 120, "SUP006"),
    ("PROD098", "Wall Mount Shelves", "Furniture", 18, 7, "SUP003"),
    ("PROD099", "HDMI Splitter", "Electronics", 65, 24, "SUP005"),
    ("PROD100", "Business Card Holder", "Supplies", 150, 60, "SUP004"),
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
    print(f"Total Products Now: {added + failed + 50}")
    print(f"{'='*50}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

import sqlite3
from datetime import datetime

def migrate_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    print("🔄 Starting database migration...")
    
    # Add new columns to products table
    new_product_columns = [
        ("unit_price", "REAL DEFAULT 0.0"),
        ("total_value", "REAL DEFAULT 0.0"),
        ("restock_date", "TEXT"),
        ("restock_time", "TEXT"),
        ("last_restock_quantity", "INTEGER DEFAULT 0"),
        ("total_restocks", "INTEGER DEFAULT 0"),
        ("manufacture_date", "TEXT"),
        ("expiry_date", "TEXT"),
        ("warehouse_location", "TEXT"),
        ("sku_code", "TEXT UNIQUE"),
        ("created_date", "TEXT"),
        ("updated_date", "TEXT"),
    ]
    
    for column_name, column_type in new_product_columns:
        try:
            cursor.execute(f"ALTER TABLE products ADD COLUMN {column_name} {column_type};")
            print(f"✅ Added column '{column_name}' to products table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"⚠️  Column '{column_name}' already exists")
            else:
                print(f"❌ Error adding '{column_name}': {e}")
    
    # Add new columns to sales_history table
    new_sales_columns = [
        ("unit_price", "REAL"),
        ("total_amount", "REAL"),
        ("sale_time", "TEXT"),
        ("customer_name", "TEXT"),
        ("payment_method", "TEXT"),
        ("notes", "TEXT"),
    ]
    
    for column_name, column_type in new_sales_columns:
        try:
            cursor.execute(f"ALTER TABLE sales_history ADD COLUMN {column_name} {column_type};")
            print(f"✅ Added column '{column_name}' to sales_history table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"⚠️  Column '{column_name}' already exists")
            else:
                print(f"❌ Error adding '{column_name}': {e}")
    
    # Add new columns to suppliers table
    new_supplier_columns = [
        ("phone_number", "TEXT"),
        ("address", "TEXT"),
        ("city", "TEXT"),
        ("country", "TEXT"),
        ("payment_terms", "TEXT"),
    ]
    
    for column_name, column_type in new_supplier_columns:
        try:
            cursor.execute(f"ALTER TABLE suppliers ADD COLUMN {column_name} {column_type};")
            print(f"✅ Added column '{column_name}' to suppliers table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"⚠️  Column '{column_name}' already exists")
            else:
                print(f"❌ Error adding '{column_name}': {e}")
    
    # Set default values for created_date
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(f"UPDATE products SET created_date = '{today}' WHERE created_date IS NULL;")
        cursor.execute(f"UPDATE products SET updated_date = '{today}' WHERE updated_date IS NULL;")
        print(f"✅ Set default timestamps for existing products")
    except Exception as e:
        print(f"⚠️  Could not set timestamps: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📊 NEW ATTRIBUTES ADDED:\n")
    print("PRODUCTS TABLE:")
    print("  • unit_price - Price per unit")
    print("  • total_value - Current stock value (stock × price)")
    print("  • restock_date - Last restock date (YYYY-MM-DD)")
    print("  • restock_time - Last restock time (HH:MM:SS)")
    print("  • last_restock_quantity - Quantity in last restock")
    print("  • total_restocks - Total number of restocks")
    print("  • manufacture_date - Manufacturing date")
    print("  • expiry_date - Product expiry date")
    print("  • warehouse_location - Storage location")
    print("  • sku_code - Unique SKU identifier")
    print("  • created_date - Product added date")
    print("  • updated_date - Last update date\n")
    
    print("SALES_HISTORY TABLE:")
    print("  • unit_price - Price per unit sold")
    print("  • total_amount - Total amount earned (quantity × price)")
    print("  • sale_time - Time of sale (HH:MM:SS)")
    print("  • customer_name - Customer name")
    print("  • payment_method - Payment method used")
    print("  • notes - Additional notes\n")
    
    print("SUPPLIERS TABLE:")
    print("  • phone_number - Supplier contact number")
    print("  • address - Supplier street address")
    print("  • city - Supplier city")
    print("  • country - Supplier country")
    print("  • payment_terms - Payment terms (Net 30, etc.)")

if __name__ == '__main__':
    migrate_db()

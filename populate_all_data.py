import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = 'inventory.db'

def populate_all_data():
    """Populate all tables with realistic synthetic data."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Product categories and base prices
    categories = {
        'Electronics': (5000, 50000),
        'Furniture': (1000, 15000),
        'Office Supplies': (10, 500),
        'Cleaning Supplies': (50, 500),
        'Tools': (200, 5000)
    }
    
    warehouses = ['Mumbai-A', 'Delhi-B', 'Bangalore-C', 'Hyderabad-D', 'Chennai-E']
    manufacturers = ['Tech Ltd', 'Furniture Co', 'Global Supply', 'Premium Inc', 'Quality Goods']
    suppliers = ['SUP001', 'SUP002', 'SUP003']
    customers = [
        'Raj Patel', 'Priya Sharma', 'Amit Kumar', 'Anjali Singh', 'Rohan Verma',
        'Neha Gupta', 'Vikram Desai', 'Sneha Reddy', 'Arjun Nair', 'Divya Menon',
        'Sanjay Pillai', 'Isha Iyer', 'Kabir Ahmed', 'Zara Khan', 'Ravi Chopra',
        'Maya Bhat', 'Karan Singh', 'Pooja Verma', 'Nikhil Sharma', 'Richa Patel'
    ]
    payment_methods = ['Cash', 'Credit Card', 'Debit Card', 'UPI', 'Bank Transfer', 'Cheque']
    
    try:
        # ===== 1. POPULATE PRODUCTS =====
        print("Step 1: Populating PRODUCTS table...")
        cursor.execute("SELECT COUNT(*) FROM products WHERE unit_price IS NULL OR unit_price = 0")
        empty_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT product_id, category FROM products")
        products = cursor.fetchall()
        
        for product_id, category in products:
            # Generate unit_price if missing
            price_range = categories.get(category, (100, 5000))
            unit_price = round(random.uniform(price_range[0], price_range[1]), 2)
            
            # Get current stock for total_value calculation
            cursor.execute("SELECT current_stock FROM products WHERE product_id = ?", (product_id,))
            stock = cursor.fetchone()[0]
            total_value = round(unit_price * stock, 2)
            
            # Generate manufacture and expiry dates
            mfg_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
            exp_date = (datetime.now() + timedelta(days=random.randint(90, 1095))).strftime('%Y-%m-%d')
            
            warehouse = random.choice(warehouses)
            created_date = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d %H:%M:%S')
            updated_date = created_date  # Will be auto-updated by triggers
            
            cursor.execute("""
                UPDATE products
                SET unit_price = ?, total_value = ?, manufacture_date = ?, expiry_date = ?,
                    warehouse_location = ?, created_date = ?, updated_date = ?
                WHERE product_id = ?
            """, (unit_price, total_value, mfg_date, exp_date, warehouse, created_date, updated_date, product_id))
        
        conn.commit()
        print(f"  ✓ Updated {len(products)} products with prices, dates, and warehouse locations")
        
        # ===== 2. POPULATE SALES_HISTORY =====
        print("\nStep 2: Populating SALES_HISTORY table...")
        cursor.execute("SELECT sale_id FROM sales_history WHERE sale_date IS NULL OR customer_name IS NULL LIMIT 1")
        needs_update = cursor.fetchone() is not None
        
        if needs_update:
            cursor.execute("SELECT sale_id, product_id, quantity_sold FROM sales_history")
            sales = cursor.fetchall()
            
            updated_sales = 0
            for sale_id, product_id, qty in sales:
                # Get product's unit_price
                cursor.execute("SELECT unit_price FROM products WHERE product_id = ?", (product_id,))
                result = cursor.fetchone()
                unit_price = result[0] if result and result[0] else random.uniform(100, 5000)
                
                total_amount = round(unit_price * qty, 2)
                customer = random.choice(customers)
                payment = random.choice(payment_methods)
                
                # Generate realistic sale date within last 90 days
                sale_date = (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d')
                sale_time = f"{random.randint(8, 21):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
                notes = random.choice(['', 'Bulk order', 'Regular customer', 'New customer', 'Urgent order', 'Delivery pending'])
                
                cursor.execute("""
                    UPDATE sales_history
                    SET unit_price = ?, total_amount = ?, customer_name = ?, payment_method = ?, 
                        sale_date = ?, sale_time = ?, notes = ?
                    WHERE sale_id = ?
                """, (unit_price, total_amount, customer, payment, sale_date, sale_time, notes, sale_id))
                
                updated_sales += 1
                if updated_sales % 500 == 0:
                    conn.commit()
                    print(f"  ✓ Updated {updated_sales} sales records...")
            
            conn.commit()
            print(f"  ✓ Updated {updated_sales} sales records with customer, payment, and amounts")
        else:
            print("  ✓ Sales history already populated")
        
        # ===== 3. POPULATE SUPPLIERS =====
        print("\nStep 3: Populating SUPPLIERS table...")
        supplier_data = [
            ('SUP001', 'TechCorp Electronics', 'contact@techcorp.com', '+91-9876543210', 
             '123 Tech Street, Mumbai', 'Mumbai', 'India', 'Net 30'),
            ('SUP002', 'Global Furniture Ltd', 'sales@globalfurniture.com', '+91-9876543211',
             '456 Furniture Avenue, Delhi', 'Delhi', 'India', 'Net 45'),
            ('SUP003', 'Office Essentials Plus', 'info@officeessentials.com', '+91-9876543212',
             '789 Supply Road, Bangalore', 'Bangalore', 'India', 'Net 15')
        ]
        
        for supplier_id, name, email, phone, address, city, country, terms in supplier_data:
            cursor.execute("""
                UPDATE suppliers
                SET supplier_name = ?, contact_email = ?, phone_number = ?, address = ?, 
                    city = ?, country = ?, payment_terms = ?
                WHERE supplier_id = ?
            """, (name, email, phone, address, city, country, terms, supplier_id))
        
        conn.commit()
        print("  ✓ Updated all 3 suppliers with complete contact details")
        
        # ===== 4. GENERATE RESTOCK EVENTS =====
        print("\nStep 4: Generating restock events...")
        cursor.execute("SELECT product_id FROM products")
        all_products = cursor.fetchall()
        
        restocked = 0
        for (product_id,) in all_products:
            # 70% chance of having restock history
            if random.random() < 0.7:
                # Generate 1-3 restock events
                num_restocks = random.randint(1, 3)
                
                for i in range(num_restocks):
                    # Restock quantities between 10-100
                    restock_qty = random.randint(10, 100)
                    restock_date = (datetime.now() - timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d')
                    restock_time = f"{random.randint(8, 17):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
                    
                    # For the latest restock event, update the product
                    if i == num_restocks - 1:
                        cursor.execute("""
                            UPDATE products
                            SET last_restock_quantity = ?, restock_date = ?, restock_time = ?, total_restocks = ?
                            WHERE product_id = ?
                        """, (restock_qty, restock_date, restock_time, num_restocks, product_id))
                
                restocked += 1
                if restocked % 20 == 0:
                    conn.commit()
                    print(f"  ✓ Generated restock events for {restocked} products...")
        
        conn.commit()
        print(f"  ✓ Generated restock events for {restocked} products")
        
        # ===== 5. RECALCULATE TOTALS =====
        print("\nStep 5: Recalculating total values...")
        cursor.execute("""
            UPDATE products
            SET total_value = ROUND(unit_price * current_stock, 2)
            WHERE unit_price > 0
        """)
        conn.commit()
        print("  ✓ Recalculated total_value for all products")
        
        print("\n" + "="*60)
        print("DATA POPULATION COMPLETE!")
        print("="*60)
        
        # Verification summary
        cursor.execute("SELECT COUNT(*) FROM products WHERE unit_price > 0")
        priced_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sales_history WHERE customer_name IS NOT NULL")
        complete_sales = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM suppliers WHERE contact_email IS NOT NULL")
        complete_suppliers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE total_restocks > 0")
        restocked_products = cursor.fetchone()[0]
        
        print(f"Products with prices: {priced_products}/99")
        print(f"Sales with customer details: {complete_sales}/2222")
        print(f"Suppliers with details: {complete_suppliers}/3")
        print(f"Products with restock history: {restocked_products}/99")
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    populate_all_data()

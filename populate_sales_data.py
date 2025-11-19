import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Get all products
cursor.execute('SELECT product_id, product_name, unit_price FROM products')
products = cursor.fetchall()

# Get existing sales
cursor.execute('SELECT sale_id, product_id, quantity_sold, sale_date FROM sales_history ORDER BY sale_id')
existing_sales = cursor.fetchall()

print(f"Found {len(products)} products")
print(f"Found {len(existing_sales)} existing sales records to update")

# Customer names
customers = [
    "Raj Patel", "Priya Sharma", "Amit Kumar", "Anjali Singh",
    "Rohan Verma", "Neha Gupta", "Vikram Desai", "Sneha Reddy",
    "Arjun Nair", "Divya Menon", "Sanjay Pillai", "Isha Iyer",
    "Kabir Ahmed", "Zara Khan", "Ravi Chopra", "Maya Bhat"
]

payment_methods = ["Cash", "Credit Card", "Debit Card", "UPI", "Bank Transfer"]

# Update existing sales with payment details
updated_count = 0
for sale_id, product_id, quantity_sold, sale_date in existing_sales:
    # Find product to get unit price
    unit_price = None
    for prod in products:
        if prod[0] == product_id:
            unit_price = prod[2]
            break
    
    if unit_price is None or unit_price == 0:
        # Use random price between 10-500
        unit_price = random.choice([10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500])
    
    total_amount = unit_price * quantity_sold
    customer_name = random.choice(customers)
    payment_method = random.choice(payment_methods)
    notes = random.choice(["", "Bulk order", "Regular customer", "New customer", "Urgent order"])
    
    cursor.execute('''
        UPDATE sales_history 
        SET unit_price = ?, total_amount = ?, customer_name = ?, payment_method = ?, notes = ?
        WHERE sale_id = ?
    ''', (unit_price, total_amount, customer_name, payment_method, notes, sale_id))
    
    updated_count += 1
    if updated_count % 100 == 0:
        print(f"Updated {updated_count} records...")

conn.commit()

# Verify updates
cursor.execute('SELECT COUNT(*) FROM sales_history WHERE total_amount > 0')
count = cursor.fetchone()[0]
print(f"\n✓ Successfully updated {updated_count} sales records")
print(f"✓ Total records with payment data: {count}")

# Show sample
cursor.execute('SELECT sale_id, product_id, quantity_sold, unit_price, total_amount, customer_name, payment_method FROM sales_history LIMIT 5')
print("\nSample updated records:")
for row in cursor.fetchall():
    print(row)

conn.close()

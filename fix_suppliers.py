import sqlite3

DB_NAME = 'inventory.db'

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Fix supplier linkage - assign products to valid suppliers (SUP001, SUP002, SUP003)
cursor.execute("""
SELECT product_id FROM products
""")
products = cursor.fetchall()

# Distribute products across 3 suppliers
suppliers = ['SUP001', 'SUP002', 'SUP003']
for idx, (product_id,) in enumerate(products):
    supplier_id = suppliers[idx % 3]  # Round-robin assignment
    cursor.execute("UPDATE products SET supplier_id = ? WHERE product_id = ?", (supplier_id, product_id))

conn.commit()

# Verify the fix
cursor.execute("""
SELECT COUNT(*) FROM products WHERE current_stock < reorder_point
""")
restock_count = cursor.fetchone()[0]

print(f"Fixed supplier linkage!")
print(f"Products needing restock: {restock_count}")

# Show the restock list
cursor.execute("""
SELECT
    p.product_id,
    p.product_name,
    p.current_stock,
    p.reorder_point,
    s.supplier_name,
    s.contact_email
FROM products AS p
JOIN suppliers AS s ON p.supplier_id = s.supplier_id
WHERE p.current_stock < p.reorder_point
ORDER BY p.current_stock ASC
""")

print("\nRestock List:")
print("-" * 80)
for row in cursor.fetchall():
    restock_qty = (row[3] * 2) - row[2]
    print(f"{row[0]}: {row[1]}")
    print(f"  Stock: {row[2]}, Reorder Point: {row[3]}, Need: {restock_qty} units")
    print(f"  Supplier: {row[4]} ({row[5]})")
    print()

conn.close()

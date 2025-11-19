import sqlite3

conn = sqlite3.connect('inventory.db')
cur = conn.cursor()

# Query common desk-lamp names and PROD002
cur.execute("""
SELECT product_id, product_name, unit_price, current_stock, total_value
FROM products
WHERE product_name LIKE '%Desk Lamp%' OR product_name LIKE '%desk lamp%' OR product_id = 'PROD002' OR product_name LIKE '%Lamp%'
LIMIT 50
""")
rows = cur.fetchall()

if not rows:
    print('No matching products found')
else:
    for r in rows:
        print(r)

conn.close()

import sqlite3
from datetime import datetime

# Example price updates for desk lamps
price_updates = {
    'PROD002': 45.0,   # Desk Lamp
    'PROD045': 55.0,   # Desk Lamp LED (Dimmable)
    'PROD065': 50.0    # Desk Lamp (Task Light)
}

conn = sqlite3.connect('inventory.db')
cur = conn.cursor()

for pid, price in price_updates.items():
    cur.execute("SELECT current_stock FROM products WHERE product_id=?", (pid,))
    r = cur.fetchone()
    if r:
        stock = r[0] or 0
        total_value = stock * price
        cur.execute("UPDATE products SET unit_price=?, total_value=?, updated_date=? WHERE product_id=?", (price, total_value, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pid))
        print(f"Updated {pid}: unit_price={price}, total_value={total_value}")
    else:
        print(f"Product {pid} not found")

conn.commit()
conn.close()

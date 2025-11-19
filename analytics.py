# analytics.py (Final and Complete Version)
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'inventory.db'

def get_db_connection():
    return sqlite3.connect(DB_NAME)

# --- Functions to retrieve data for the LLM and the public dashboard ---
def get_all_inventory_data():
    """Retrieves all relevant data and formats it for the LLM."""
    with get_db_connection() as conn:
        products_df = pd.read_sql_query("SELECT * FROM products", conn)
        sales_df = pd.read_sql_query(
            "SELECT product_id, quantity_sold, unit_price, total_amount, sale_date, customer_name, payment_method FROM sales_history ORDER BY sale_date DESC LIMIT 50", 
            conn
        )
        
        # Calculate payment summary
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_transaction,
                MAX(total_amount) as largest_sale
            FROM sales_history
        """)
        summary = cursor.fetchone()
        
        cursor.execute("""
            SELECT customer_name, COUNT(*) as transaction_count, SUM(total_amount) as customer_total
            FROM sales_history
            WHERE customer_name IS NOT NULL
            GROUP BY customer_name
            ORDER BY customer_total DESC
            LIMIT 10
        """)
        top_customers = cursor.fetchall()
        
        inventory_data_text = (
            "=== PRODUCTS INVENTORY ===\n"
            + products_df.to_string(index=False)
            + "\n\n"
            + "=== PAYMENT & REVENUE SUMMARY ===\n"
            f"Total Transactions: {summary[0]}\n"
            f"Total Revenue: ₹{summary[1]:,.2f}\n"
            f"Average Transaction: ₹{summary[2]:,.2f}\n"
            f"Largest Sale: ₹{summary[3]:,.2f}\n"
            + "\n"
            + "=== TOP 10 CUSTOMERS BY TOTAL PURCHASES ===\n"
        )
        
        for customer_name, count, total in top_customers:
            inventory_data_text += f"- {customer_name}: {count} purchases, Total: ₹{total:,.2f}\n"
        
        inventory_data_text += (
            "\n=== RECENT SALES (Last 50 Transactions) ===\n"
            + sales_df.to_string(index=False)
        )
        return inventory_data_text

def get_low_stock_alerts():
    """Returns a DataFrame of products with stock below their reorder point."""
    with get_db_connection() as conn:
        query = "SELECT product_name, current_stock, reorder_point FROM products WHERE current_stock < reorder_point"
        df = pd.read_sql_query(query, conn)
        return df

def get_top_sellers(num_products=5):
    """Finds the top N best-selling products from sales history."""
    with get_db_connection() as conn:
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        query = f"""
            SELECT p.product_name, SUM(s.quantity_sold) as total_sales
            FROM sales_history s
            JOIN products p ON s.product_id = p.product_id
            WHERE s.sale_date >= '{thirty_days_ago}'
            GROUP BY p.product_name
            ORDER BY total_sales DESC
            LIMIT {num_products}
        """
        df = pd.read_sql_query(query, conn)
        return df

# --- Functions for Owner Tools ---
def get_reorder_list():
    """Returns a DataFrame of low-stock items with supplier and restock quantity."""
    with get_db_connection() as conn:
        query = """
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
        """
        reorder_df = pd.read_sql_query(query, conn)
        
        # Calculate the restock quantity
        reorder_df['restock_quantity'] = (reorder_df['reorder_point'] * 2) - reorder_df['current_stock']
        
        return reorder_df

def get_low_stock_items_for_llm():
    """Retrieves and formats only the low-stock items for the LLM."""
    with get_db_connection() as conn:
        query = "SELECT product_name, current_stock, reorder_point FROM products WHERE current_stock < reorder_point"
        low_stock_df = pd.read_sql_query(query, conn)
        
        if not low_stock_df.empty:
            return low_stock_df.to_string(index=False)
        else:
            return "There are no items that need to be restocked at this time."

def add_new_product(product_id, product_name, category, current_stock, reorder_point, supplier_id):
    """Adds a new product to the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO products (product_id, product_name, category, current_stock, reorder_point, supplier_id) VALUES (?, ?, ?, ?, ?, ?)",
                (product_id, product_name, category, current_stock, reorder_point, supplier_id)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

def delete_product(product_id):
    """Deletes a product and its sales history from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM sales_history WHERE product_id = ?", (product_id,))
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred during deletion: {e}")
            return False

def restock_products(restock_list):
    """Restocks products in the database with the specified quantities.
    Also updates restock metadata: last_restock_quantity, restock_date, restock_time,
    and increments total_restocks. This ensures the LLM can report recent restocks.
    """
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            for product_id, quantity_to_add in restock_list.items():
                # update current stock
                cursor.execute(
                    "UPDATE products SET current_stock = current_stock + ? WHERE product_id = ?",
                    (quantity_to_add, product_id)
                )

                # read existing total_restocks (may be NULL)
                cursor.execute("SELECT total_restocks FROM products WHERE product_id = ?", (product_id,))
                row = cursor.fetchone()
                total_restocks = row[0] if row and row[0] is not None else 0
                total_restocks = total_restocks + 1

                # update restock metadata
                cursor.execute(
                    """
                    UPDATE products
                    SET last_restock_quantity = ?, restock_date = ?, restock_time = ?, total_restocks = ?
                    WHERE product_id = ?
                    """,
                    (quantity_to_add, date_str, time_str, total_restocks, product_id)
                )

            conn.commit()
            return True
        except Exception as e:
            print(f"An error occurred during restocking: {e}")
            return False
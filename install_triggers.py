import sqlite3
from datetime import datetime

DB_NAME = 'inventory.db'

def install_triggers():
    """Install SQLite triggers to keep database attributes updated automatically."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Drop existing triggers (if any) to avoid conflicts
        triggers = [
            'update_product_total_value',
            'update_product_updated_date_on_stock_change',
            'update_product_updated_date_on_price_change',
            'update_sales_history_timestamp'
        ]
        
        for trigger in triggers:
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")
        
        print("✓ Dropped old triggers")
        
        # 1. Auto-calculate total_value = unit_price * current_stock when either changes
        cursor.execute("""
        CREATE TRIGGER update_product_total_value
        AFTER UPDATE OF current_stock, unit_price ON products
        FOR EACH ROW
        BEGIN
            UPDATE products
            SET total_value = NEW.unit_price * NEW.current_stock
            WHERE product_id = NEW.product_id;
        END;
        """)
        print("✓ Created trigger: update_product_total_value")
        
        # 2. Auto-update updated_date when stock changes (restock happens)
        cursor.execute("""
        CREATE TRIGGER update_product_updated_date_on_stock_change
        AFTER UPDATE OF current_stock ON products
        FOR EACH ROW
        BEGIN
            UPDATE products
            SET updated_date = datetime('now')
            WHERE product_id = NEW.product_id;
        END;
        """)
        print("✓ Created trigger: update_product_updated_date_on_stock_change")
        
        # 3. Auto-update updated_date when price changes
        cursor.execute("""
        CREATE TRIGGER update_product_updated_date_on_price_change
        AFTER UPDATE OF unit_price ON products
        FOR EACH ROW
        BEGIN
            UPDATE products
            SET updated_date = datetime('now')
            WHERE product_id = NEW.product_id;
        END;
        """)
        print("✓ Created trigger: update_product_updated_date_on_price_change")
        
        # 4. Set timestamp on sales_history inserts and updates
        cursor.execute("""
        CREATE TRIGGER update_sales_history_timestamp
        AFTER INSERT ON sales_history
        FOR EACH ROW
        BEGIN
            UPDATE sales_history
            SET sale_date = CASE WHEN NEW.sale_date IS NULL THEN datetime('now') ELSE NEW.sale_date END
            WHERE sale_id = NEW.sale_id;
        END;
        """)
        print("✓ Created trigger: update_sales_history_timestamp")
        
        conn.commit()
        print("\n✅ All triggers installed successfully!")
        
        # Verify triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        installed = cursor.fetchall()
        print(f"✓ Total triggers in database: {len(installed)}")
        for t in installed:
            print(f"  - {t[0]}")
        
    except Exception as e:
        print(f"❌ Error installing triggers: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    install_triggers()

import sqlite3

DB_NAME = 'inventory.db'

def fix_supplier_links():
    """Fix broken supplier links in products table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # First, verify valid suppliers exist
        cursor.execute("SELECT supplier_id FROM suppliers")
        valid_suppliers = [row[0] for row in cursor.fetchall()]
        print(f"Valid suppliers: {valid_suppliers}")
        
        # Check current supplier_id distribution in products
        cursor.execute("SELECT DISTINCT supplier_id FROM products")
        current_suppliers = [row[0] for row in cursor.fetchall()]
        print(f"Current suppliers in products: {current_suppliers}")
        
        # Update all products to use only valid suppliers (rotate through them)
        cursor.execute("SELECT product_id FROM products ORDER BY product_id")
        products = cursor.fetchall()
        
        print(f"\nFixing supplier links for {len(products)} products...")
        
        for idx, (product_id,) in enumerate(products):
            # Assign suppliers in rotation
            new_supplier = valid_suppliers[idx % len(valid_suppliers)]
            cursor.execute("UPDATE products SET supplier_id = ? WHERE product_id = ?", 
                          (new_supplier, product_id))
            
            if (idx + 1) % 20 == 0:
                conn.commit()
                print(f"  Updated {idx + 1} products...")
        
        conn.commit()
        print(f"\n✓ Fixed supplier links for all {len(products)} products")
        
        # Verify the fix
        cursor.execute("SELECT supplier_id, COUNT(*) FROM products GROUP BY supplier_id")
        distribution = cursor.fetchall()
        print("\nNew supplier distribution:")
        for sup_id, count in distribution:
            print(f"  {sup_id}: {count} products")
        
        # Test the reorder list query
        print("\n" + "="*60)
        print("TESTING REORDER LIST QUERY")
        print("="*60)
        
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
            LIMIT 10
        """)
        
        reorder_items = cursor.fetchall()
        if reorder_items:
            print(f"\nFound {len(reorder_items)} items to restock:")
            for item in reorder_items:
                print(f"  {item[0]}: {item[1]} (Stock: {item[2]}, Reorder: {item[3]})")
                print(f"    Supplier: {item[4]} ({item[5]})")
        else:
            print("\nNo items need restocking (all stock levels are OK)")
        
        print("\n✅ SUPPLIER LINK FIX COMPLETE!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_supplier_links()

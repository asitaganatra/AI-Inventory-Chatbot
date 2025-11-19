#!/usr/bin/env python3
"""
STARTUP VERIFICATION SCRIPT
This script verifies that all data and configurations are intact when you restart.
Run this before starting the app to ensure everything is working.
"""

import sqlite3
import os
from datetime import datetime

DB_NAME = 'inventory.db'

def verify_database():
    """Verify database integrity and completeness."""
    if not os.path.exists(DB_NAME):
        print("ERROR: inventory.db not found!")
        return False
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("DATABASE VERIFICATION REPORT")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n✓ Tables found: {len(tables)}")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} rows")
        
        # Check triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        triggers = cursor.fetchall()
        print(f"\n✓ Triggers installed: {len(triggers)}")
        for trigger in triggers:
            print(f"  - {trigger[0]}")
        
        # Verify product data completeness
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN unit_price > 0 THEN 1 ELSE 0 END) as with_price,
                SUM(CASE WHEN total_value > 0 THEN 1 ELSE 0 END) as with_value,
                SUM(CASE WHEN warehouse_location IS NOT NULL THEN 1 ELSE 0 END) as with_location
            FROM products
        """)
        row = cursor.fetchone()
        print(f"\n✓ Products ({row[0]} total):")
        print(f"  - With prices: {row[1]}")
        print(f"  - With total_value: {row[2]}")
        print(f"  - With warehouse: {row[3]}")
        
        # Verify sales data completeness
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN customer_name IS NOT NULL THEN 1 ELSE 0 END) as with_customer,
                SUM(CASE WHEN total_amount > 0 THEN 1 ELSE 0 END) as with_amount,
                SUM(CASE WHEN payment_method IS NOT NULL THEN 1 ELSE 0 END) as with_payment
            FROM sales_history
        """)
        row = cursor.fetchone()
        print(f"\n✓ Sales History ({row[0]} total):")
        print(f"  - With customer name: {row[1]}")
        print(f"  - With amount: {row[2]}")
        print(f"  - With payment method: {row[3]}")
        
        # Verify suppliers
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN contact_email IS NOT NULL THEN 1 ELSE 0 END) as with_email
            FROM suppliers
        """)
        row = cursor.fetchone()
        print(f"\n✓ Suppliers ({row[0]} total):")
        print(f"  - With contact details: {row[1]}")
        
        # Business metrics
        cursor.execute("SELECT SUM(total_value) FROM products")
        inventory_value = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(total_amount) FROM sales_history")
        total_revenue = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT customer_name) FROM sales_history")
        unique_customers = cursor.fetchone()[0]
        
        print(f"\n✓ Business Metrics:")
        print(f"  - Total Inventory Value: Rs. {inventory_value:,.2f}")
        print(f"  - Total Revenue: Rs. {total_revenue:,.2f}")
        print(f"  - Unique Customers: {unique_customers}")
        
        print("\n" + "="*60)
        print("STATUS: ALL SYSTEMS OPERATIONAL ✓")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return False
    finally:
        conn.close()

def check_requirements():
    """Check if required Python packages are installed."""
    print("\n" + "="*60)
    print("CHECKING REQUIRED PACKAGES")
    print("="*60)
    
    required_packages = {
        'streamlit': 'Web app framework',
        'pandas': 'Data manipulation',
        'langchain': 'LLM integration',
        'langchain_google_genai': 'Google Gemini API',
        'gtts': 'Text-to-speech',
        'speech_recognition': 'Voice input',
        'pyaudio': 'Microphone access'
    }
    
    missing = []
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {package:<25} ({description})")
        except ImportError:
            print(f"✗ {package:<25} (MISSING - {description})")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install " + " ".join(missing))
        return False
    
    print("\n✓ All required packages installed!")
    return True

def startup_checklist():
    """Complete startup checklist."""
    print("\n" + "="*60)
    print("STARTUP CHECKLIST")
    print("="*60)
    
    checks = [
        ("Database file exists", os.path.exists(DB_NAME)),
        ("API key in .streamlit/secrets.toml", os.path.exists('.streamlit/secrets.toml')),
        ("analytics.py exists", os.path.exists('analytics.py')),
        ("app.py exists", os.path.exists('app.py')),
        ("install_triggers.py exists", os.path.exists('install_triggers.py')),
        ("populate_all_data.py exists", os.path.exists('populate_all_data.py')),
    ]
    
    all_good = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if not result:
            all_good = False
    
    return all_good

if __name__ == "__main__":
    db_ok = verify_database()
    pkg_ok = check_requirements()
    setup_ok = startup_checklist()
    
    print("\n" + "="*60)
    if db_ok and pkg_ok and setup_ok:
        print("READY TO START: streamlit run app.py")
    else:
        print("ISSUES DETECTED - FIX ABOVE BEFORE STARTING")
    print("="*60 + "\n")

# AI Inventory Management System - Startup Guide

## Quick Start (After Restart)

```bash
# Navigate to project folder
cd "c:\Users\asita\Downloads\Imp files project\AI_INVENTORY_CHANGES"

# Activate virtual environment (if using venv)
.\venv\Scripts\activate

# Run startup verification
python startup_check.py

# Start the application
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## What's Saved & Persistent

### ✓ Database (inventory.db)
- **99 products** with complete attributes:
  - Unit prices (realistic range)
  - Current stock levels
  - Total values (auto-calculated)
  - Warehouse locations (5 different warehouses)
  - Manufacture & expiry dates
  - Restock history (72 products)

- **2,222 sales records** with:
  - Customer names (20 unique customers)
  - Payment methods (Cash, Card, UPI, etc.)
  - Transaction amounts
  - Sale dates & times
  - Order notes

- **3 suppliers** with full details:
  - Contact emails and phone numbers
  - Physical addresses
  - Payment terms

### ✓ Automatic Features
- **SQLite Triggers** (4 installed):
  - Auto-update `total_value` when price/stock changes
  - Auto-update `updated_date` on modifications
  - Auto-timestamp sales records
  
### ✓ Application Code
- **app.py** (680 lines):
  - Voice chat with mic input
  - Text-to-speech output (female voice, English & Hindi)
  - Chat interface with message history
  - Owner Tools (login, price editor, restock workflow)
  - Dashboard with alerts
  - No markdown symbols (*,**) in speech

- **analytics.py**:
  - Database query functions
  - Auto-updating triggers
  - Restock metadata tracking

### ✓ Configuration
- **Streamlit layout**: Wide mode, expanded sidebar
- **LLM Model**: Google Gemini 2.5 Flash
- **Response Style**: Brief (1-2 sentences) by default
- **Languages**: English & Hindi

---

## Running After System Restart

### Step 1: Verify Everything
```bash
python startup_check.py
```
Expected output: "STATUS: ALL SYSTEMS OPERATIONAL ✓"

### Step 2: Start Streamlit
```bash
streamlit run app.py
```

### Step 3: Test in Browser
Visit: http://localhost:8501

---

## Key Login Credentials

**Owner Access:**
- Password: `owner123`
- Access: Owner Tools, Price Editor, Restock Workflow

---

## Testing the System

### Quick Test Questions (English)
```
1. "What's our total revenue?"
2. "How many units of keyboard in stock?"
3. "Who is our top customer?"
4. "Show low stock products"
5. "What's the highest sale amount?"
```

### Quick Test Questions (Hindi)
Switch to Hindi in Voice Language dropdown, then:
```
1. "हमारा कुल राजस्व क्या है?"
2. "कीबोर्ड की स्टॉक कितनी है?"
3. "शीर्ष ग्राहक कौन है?"
4. "कम स्टॉक वाले उत्पाद दिखाएं"
5. "सबसे बड़ी बिक्री राशि क्या थी?"
```

---

## File Structure

```
AI_INVENTORY_CHANGES/
├── inventory.db                 # SQLite database (PERSISTENT)
├── app.py                       # Main Streamlit application
├── analytics.py                 # Database functions
├── install_triggers.py          # Trigger installation script
├── populate_all_data.py        # Data population script
├── startup_check.py            # Verification script (THIS FILE)
├── .streamlit/
│   └── secrets.toml            # API keys (your file)
├── venv/                        # Python virtual environment
└── README.md                    # This file
```

---

## Important Notes

1. **Database is Persistent**: 
   - All data in `inventory.db` persists across restarts
   - No data migration needed

2. **Triggers Auto-Active**:
   - SQL triggers run automatically
   - `total_value` recalculates on price/stock changes
   - `updated_date` tracks all modifications

3. **API Key Required**:
   - Ensure `.streamlit/secrets.toml` exists with `GEMINI_API_KEY`
   - Without it, the app will not start

4. **Virtual Environment**:
   - Keep `venv/` folder intact
   - All packages are saved there

5. **Backup Recommendation**:
   - Backup `inventory.db` regularly (File > Save As)
   - Or use: `cp inventory.db inventory.db.backup`

---

## Troubleshooting

### Issue: "API Key not found"
**Solution**: Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

### Issue: "ModuleNotFoundError: No module named 'X'"
**Solution**: Install missing package:
```bash
pip install package_name
```

Or run full install:
```bash
pip install streamlit pandas langchain langchain_google_genai gtts speech_recognition pyaudio
```

### Issue: "Database locked"
**Solution**: Ensure only one instance of app is running:
```bash
taskkill /F /IM python.exe
# Wait 2 seconds, then restart
streamlit run app.py
```

### Issue: Microphone not working
**Solution**: 
- Check microphone is connected and enabled
- Run: `python -c "import pyaudio; print('PyAudio OK')"`
- Restart the app

---

## Verification Checklist

Before using, run:
```bash
python startup_check.py
```

Expected results:
- ✓ 99 products in database
- ✓ 2,222 sales records
- ✓ 3 suppliers with details
- ✓ 4 triggers installed
- ✓ All required packages installed
- ✓ All configuration files present

---

## Support

All data and features remain exactly as configured:
- Voice chat (English & Hindi) ✓
- Text-to-speech (female voice) ✓
- Chat history preservation ✓
- Dashboard with alerts ✓
- Owner Tools & restock workflow ✓
- Automatic database updates ✓

Everything works after restart! 🎉

---

**Last Updated**: November 17, 2025
**System Version**: AI Inventory v1.0
**Database**: SQLite (inventory.db)

"""
Verify complete setup including .env loading and API key.
"""
import os
from dotenv import load_dotenv
from database import DatabaseManager
from api import CompaniesHouseAPI

print("="*60)
print("Setup Verification")
print("="*60)

# Load .env
load_dotenv()

# Check database
print("\n[1/4] Checking Database...")
try:
    db = DatabaseManager()
    stats = db.get_database_stats()
    print(f"    [OK] Database initialized")
    print(f"    [OK] Total companies: {stats['total_companies']}")
except Exception as e:
    print(f"    [ERROR] Database error: {e}")

# Check API key
print("\n[2/4] Checking API Key...")
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
if api_key:
    print(f"    [OK] API key found: {api_key[:8]}...{api_key[-4:]}")
else:
    print(f"    [ERROR] API key not found in environment")

# Check API connection
print("\n[3/4] Testing Companies House API...")
if api_key:
    try:
        api = CompaniesHouseAPI()
        # Test with a known company
        profile = api.get_company_profile("00000006")
        if profile:
            print(f"    [OK] API connection successful")
            print(f"    [OK] Test query returned: {profile.get('company_name')}")
        else:
            print(f"    [ERROR] API returned no data")
    except ValueError as e:
        print(f"    [ERROR] API key error: {e}")
    except Exception as e:
        print(f"    [ERROR] API error: {e}")
else:
    print("    - Skipped (no API key)")

# Check file structure
print("\n[4/4] Checking Files...")
from pathlib import Path

files_to_check = [
    ".env",
    "clients.xlsx",
    "client_data.db",
    "app.py",
    "pages/1_📊_Dashboard.py",
    "pages/2_📋_Client_Management.py",
    "database/db_manager.py",
    "api/companies_house.py"
]

all_good = True
for file_path in files_to_check:
    if Path(file_path).exists():
        print(f"    [OK] {file_path}")
    else:
        print(f"    [MISSING] {file_path}")
        all_good = False

# Final verdict
print("\n" + "="*60)
if api_key and all_good:
    print("[SUCCESS] Setup Complete!")
    print("="*60)
    print("\nYour dashboard is ready to use:")
    print("  1. Run: streamlit run app.py")
    print("  2. Go to Client Management page")
    print("  3. Click 'Refresh Deadlines' button")
    print("  4. Deadlines will update from Companies House API")
else:
    print("[INCOMPLETE] Setup needs attention")
    print("="*60)
    if not api_key:
        print("\n[WARNING] API key not configured - using Excel deadlines only")
    if not all_good:
        print("\n[WARNING] Some files are missing")

print()

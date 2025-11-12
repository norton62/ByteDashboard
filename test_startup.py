"""
Quick test to verify all modules load correctly
"""
import sys
from pathlib import Path

print("Testing module imports...")

try:
    from database import DatabaseManager
    print("[OK] Database module loaded")

    from api import CompaniesHouseAPI
    print("[OK] API module loaded")

    # Test database initialization
    db = DatabaseManager()
    stats = db.get_database_stats()
    print(f"[OK] Database initialized: {stats['total_companies']} companies")

    print("\n[SUCCESS] All modules loaded successfully!")
    print("\nYou can now run the application with:")
    print("  streamlit run app.py")

except Exception as e:
    print(f"\n[ERROR] Failed to load modules: {e}")
    sys.exit(1)

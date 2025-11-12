"""
Reset Database Utility
Clears all data from the database and optionally re-imports from Excel.
"""
import os
from pathlib import Path
from database import DatabaseManager

def reset_database(reimport_excel=True):
    """Reset the database by deleting and recreating it.

    Args:
        reimport_excel: If True, automatically imports from clients.xlsx after reset
    """
    db_path = Path("client_data.db")

    print("=" * 60)
    print("DATABASE RESET UTILITY")
    print("=" * 60)

    # Check if database exists
    if db_path.exists():
        print(f"\n[INFO] Found existing database: {db_path}")

        # Get current stats before deletion
        try:
            db = DatabaseManager()
            stats = db.get_database_stats()
            print(f"       Current database contains: {stats['total_companies']} companies")
        except:
            print("       (Unable to read current database)")

        # Delete the database file
        try:
            os.remove(db_path)
            print(f"[SUCCESS] Deleted database file")
        except Exception as e:
            print(f"[ERROR] Failed to delete database: {e}")
            return False
    else:
        print("\n[INFO] No existing database found")

    # Create fresh database
    print("\n[INFO] Creating fresh database...")
    db = DatabaseManager()
    print("[SUCCESS] New database created with empty schema")

    # Re-import from Excel if requested
    if reimport_excel:
        excel_file = Path("clients.xlsx")

        if not excel_file.exists():
            print(f"\n[WARNING] Excel file not found: {excel_file}")
            print("          Database is empty. Add clients.xlsx and run this script again.")
            return True

        print(f"\n[INFO] Importing data from {excel_file}...")
        try:
            count = db.import_from_excel(str(excel_file))
            print(f"[SUCCESS] Imported {count} companies from Excel")

            # Show summary
            stats = db.get_database_stats()
            print(f"\n[SUMMARY]")
            print(f"  Total Companies: {stats['total_companies']}")
            print(f"  Accounts Filed: {stats['filed_count']}")
            print(f"  Accounts Not Filed: {stats['unfiled_count']}")

            return True

        except Exception as e:
            print(f"[ERROR] Failed to import from Excel: {e}")
            import traceback
            traceback.print_exc()
            return False

    return True

if __name__ == "__main__":
    print("\nThis will DELETE all existing data and re-import from clients.xlsx")
    response = input("\nAre you sure you want to continue? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        success = reset_database(reimport_excel=True)

        if success:
            print("\n" + "=" * 60)
            print("[COMPLETE] Database has been reset successfully!")
            print("=" * 60)
            print("\nYou can now run the application:")
            print("  streamlit run app.py")
        else:
            print("\n[FAILED] Database reset encountered errors")
    else:
        print("\n[CANCELLED] No changes made to the database")

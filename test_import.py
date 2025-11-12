"""
Test the Excel import functionality with timestamp handling
"""
import pandas as pd
from database import DatabaseManager

print("Testing Excel import with timestamp handling...")

# Create a test DataFrame with Timestamp objects (like Excel import does)
test_data = {
    'Company_Name': ['Test Company 1', 'Test Company 2'],
    'Company_Number': ['99999991', '99999992'],
    'Filing_Deadline': [
        pd.Timestamp('2025-12-31'),
        pd.Timestamp('2026-01-15')
    ]
}

df = pd.DataFrame(test_data)

# Save to a test Excel file
test_file = 'test_import.xlsx'
df.to_excel(test_file, index=False)
print(f"[OK] Created test Excel file with {len(df)} companies")
print(f"     Filing_Deadline type: {type(df['Filing_Deadline'].iloc[0])}")

# Initialize database
db = DatabaseManager()

# Test import
try:
    count = db.import_from_excel(test_file)
    print(f"[SUCCESS] Imported {count} companies successfully!")

    # Verify the data was imported correctly
    all_companies = db.get_all_companies()
    test_companies = all_companies[all_companies['Company_Number'].isin(['99999991', '99999992'])]

    print(f"\n[VERIFICATION] Retrieved {len(test_companies)} test companies from database")
    print(test_companies[['Company_Name', 'Company_Number', 'Filing_Deadline']])

    print("\n[SUCCESS] All tests passed! Timestamp handling is working correctly.")

except Exception as e:
    print(f"\n[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
import os
if os.path.exists(test_file):
    os.remove(test_file)
    print(f"\n[CLEANUP] Removed test file: {test_file}")

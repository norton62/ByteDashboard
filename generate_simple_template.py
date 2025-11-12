"""
Generate a simple Excel template for importing companies.
Only requires Company Name and Number - deadlines fetched from API.
"""
import pandas as pd

# Create a simple template with just the required fields
template_data = {
    'Company_Name': [
        'Example Company Ltd',
        'Another Business Ltd',
        'Sample Corporation'
    ],
    'Company_Number': [
        '12345678',
        '87654321',
        '11223344'
    ]
}

df = pd.DataFrame(template_data)

# Save to Excel
template_file = "clients_template.xlsx"
df.to_excel(template_file, index=False)

print(f"[SUCCESS] Created {template_file}")
print(f"\nThis template only requires:")
print("  - Company_Name: The company name")
print("  - Company_Number: 8-digit company registration number")
print("\nFiling deadlines will be fetched automatically from Companies House API")
print("when you import (if API key is configured)")
print("\nYou can also include a Filing_Deadline column if you want to use")
print("Excel deadlines as a fallback (format: YYYY-MM-DD)")

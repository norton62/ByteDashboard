"""
Script to generate dummy Excel data for initial setup.
Run this once to create the clients.xlsx file.
"""
import pandas as pd
from datetime import datetime, timedelta
import random

# Generate dummy company data
companies = []
company_names = [
    "Tech Solutions Ltd",
    "Green Energy Co",
    "Global Trading Partners",
    "Innovation Ventures",
    "Manufacturing Excellence Ltd",
    "Digital Marketing Agency",
    "Financial Services Group",
    "Healthcare Systems Ltd",
    "Property Development Co",
    "Retail Solutions Ltd",
    "Transport Logistics Group",
    "Education Services Ltd",
    "Consulting Partners",
    "Software Development Ltd",
    "Construction Holdings",
    "Food & Beverage Co",
    "Telecommunications Ltd",
    "Insurance Brokers Group",
    "Media Productions Ltd",
    "Engineering Solutions"
]

# Generate company numbers (format: 8 digits)
for i, name in enumerate(company_names, start=1):
    company_number = f"{12345000 + i:08d}"

    # Generate random filing deadlines between now and 31/07/2026
    base_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 7, 31)
    days_diff = (end_date - base_date).days
    random_days = random.randint(0, days_diff)
    filing_deadline = base_date + timedelta(days=random_days)

    companies.append({
        "Company_Name": name,
        "Company_Number": company_number,
        "Filing_Deadline": filing_deadline.strftime("%Y-%m-%d")
    })

# Create DataFrame
df = pd.DataFrame(companies)

# Save to Excel
df.to_excel("clients.xlsx", index=False)
print(f"[SUCCESS] Created clients.xlsx with {len(companies)} companies")
print(f"  Columns: {', '.join(df.columns)}")
print(f"\nSample data:")
print(df.head())

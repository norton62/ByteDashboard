"""
Quick test to check if a specific company has deadline information.
"""
import os
from dotenv import load_dotenv
from api import CompaniesHouseAPI

# Load environment variables from .env file
load_dotenv()

# Check API key
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
if not api_key:
    print("[ERROR] No API key found. Set COMPANIES_HOUSE_API_KEY environment variable.")
    exit(1)

print(f"API Key configured: {api_key[:8]}...")

# Initialize API
api = CompaniesHouseAPI()

# Test with one of the problem companies
test_company = "12080057"

print(f"\nTesting company: {test_company}")
print("="*50)

# Get profile
profile = api.get_company_profile(test_company)

if profile:
    print(f"Company Name: {profile.get('company_name')}")
    print(f"Status: {profile.get('company_status')}")
    print(f"Type: {profile.get('type')}")

    accounts = profile.get('accounts', {})
    print(f"\nAccounts section exists: {bool(accounts)}")

    if accounts:
        print(f"Next due: {accounts.get('next_due', 'NOT FOUND')}")
        print(f"Overdue: {accounts.get('overdue')}")
        print(f"\nAll accounts keys: {list(accounts.keys())}")
    else:
        print("No accounts section in API response!")

    # Test get_filing_deadline with verbose
    print("\n" + "="*50)
    print("Testing get_filing_deadline():")
    print("="*50)
    deadline = api.get_filing_deadline(test_company, verbose=True)

    if deadline:
        print(f"\n[SUCCESS] Deadline: {deadline}")
    else:
        print(f"\n[FAILED] No deadline found")
else:
    print("[ERROR] Could not fetch company profile")

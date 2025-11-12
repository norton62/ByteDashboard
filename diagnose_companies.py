"""
Diagnostic tool to check Companies House API responses for specific companies.
"""
import os
import sys
from dotenv import load_dotenv
from api import CompaniesHouseAPI

# Load environment variables from .env file
load_dotenv()

def diagnose_company(api, company_number):
    """Diagnose API response for a single company."""
    print(f"\n{'='*60}")
    print(f"Diagnosing Company: {company_number}")
    print(f"{'='*60}")

    # Get full profile
    profile = api.get_company_profile(company_number)

    if not profile:
        print("[ERROR] Could not fetch company profile")
        print("Possible reasons:")
        print("  - Company number is incorrect")
        print("  - Company doesn't exist at Companies House")
        print("  - API key is invalid")
        print("  - Network connectivity issue")
        return

    # Display key information
    print(f"\nCompany Name: {profile.get('company_name', 'N/A')}")
    print(f"Company Status: {profile.get('company_status', 'N/A')}")
    print(f"Company Type: {profile.get('type', 'N/A')}")
    print(f"Incorporated: {profile.get('date_of_creation', 'N/A')}")

    # Check accounts section
    accounts = profile.get('accounts', {})

    if not accounts:
        print("\n[WARNING] No 'accounts' section in API response")
        print("This company may not be required to file accounts")
        return

    print(f"\n--- Accounts Information ---")
    print(f"Next Due: {accounts.get('next_due', '[NOT AVAILABLE]')}")
    print(f"Overdue: {accounts.get('overdue', False)}")

    # Last accounts
    last_accounts = accounts.get('last_accounts', {})
    if last_accounts:
        print(f"\nLast Accounts:")
        print(f"  Made Up To: {last_accounts.get('made_up_to', 'N/A')}")
        print(f"  Type: {last_accounts.get('type', 'N/A')}")
    else:
        print(f"\nLast Accounts: None filed yet")

    # Next accounts
    next_accounts = accounts.get('next_accounts', {})
    if next_accounts:
        print(f"\nNext Accounts:")
        print(f"  Due On: {next_accounts.get('due_on', 'N/A')}")
        print(f"  Overdue: {next_accounts.get('overdue', False)}")
        print(f"  Period End: {next_accounts.get('period_end_on', 'N/A')}")

    # Accounting reference date
    acc_ref_date = accounts.get('accounting_reference_date', {})
    if acc_ref_date:
        print(f"\nAccounting Reference Date:")
        print(f"  Day: {acc_ref_date.get('day', 'N/A')}")
        print(f"  Month: {acc_ref_date.get('month', 'N/A')}")

    # Show all available fields
    print(f"\n--- All Available Accounts Fields ---")
    for key in accounts.keys():
        print(f"  - {key}")

    # Test deadline fetch
    print(f"\n--- Testing get_filing_deadline() ---")
    deadline = api.get_filing_deadline(company_number, verbose=True)

    if deadline:
        print(f"\n[SUCCESS] Deadline found: {deadline}")
    else:
        print(f"\n[FAILED] No deadline available")
        print("\nPossible reasons:")
        print("  - Company is dissolved/liquidated")
        print("  - Company is exempt from filing")
        print("  - No next_due field in API response")
        print("  - Company hasn't filed first accounts yet")

    print(f"\n{'='*60}\n")


def main():
    """Main diagnostic function."""
    # Check for API key
    api_key = os.getenv("COMPANIES_HOUSE_API_KEY")

    if not api_key:
        print("[ERROR] COMPANIES_HOUSE_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  1. Create .env file with: COMPANIES_HOUSE_API_KEY=your_key")
        print("  2. Or set environment variable before running")
        sys.exit(1)

    print(f"API Key: {api_key[:8]}..." + "*" * 20)

    # Initialize API
    try:
        api = CompaniesHouseAPI()
        print("[OK] API initialized successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to initialize API: {e}")
        sys.exit(1)

    # Companies to diagnose (from user's error list)
    problem_companies = [
        '12080057',
        '10487129',
        '12351319',
        '13160134',
        '12599495',
        '15558346',
        '16695209',
        '15287170'
    ]

    print(f"Will diagnose {len(problem_companies)} companies...")
    print("This may take a minute...\n")

    # Diagnose each company
    for company_number in problem_companies:
        diagnose_company(api, company_number)

    print("\n" + "="*60)
    print("Diagnosis Complete!")
    print("="*60)
    print("\nCheck the output above to see why deadlines are unavailable.")
    print("Common reasons:")
    print("  - Company is dissolved or in liquidation")
    print("  - Company hasn't filed first accounts yet")
    print("  - Company is exempt from filing")
    print("  - API doesn't provide next_due for this company type")


if __name__ == "__main__":
    main()

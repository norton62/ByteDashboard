"""
Test Companies House API key validity.
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*60)
print("Companies House API Key Test")
print("="*60)

# Check if API key exists
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")

if not api_key:
    print("\n[ERROR] COMPANIES_HOUSE_API_KEY not found in environment")
    print("\nPlease check:")
    print("  1. .env file exists in current directory")
    print("  2. .env file contains: COMPANIES_HOUSE_API_KEY=your_key")
    print("  3. No spaces around the = sign")
    exit(1)

print(f"\n[OK] API Key found: {api_key[:8]}..." + "*" * 20)
print(f"     Length: {len(api_key)} characters")

# Check for common issues
if api_key.startswith(" ") or api_key.endswith(" "):
    print("\n[WARNING] API key has leading/trailing spaces!")
    api_key = api_key.strip()
    print(f"[INFO] Trimmed to: {api_key[:8]}...")

# Test API key with Companies House
print("\n" + "="*60)
print("Testing API Key with Companies House...")
print("="*60)

# Try a simple API request
test_company = "00000006"  # Royal Mail - a well-known active company
url = f"https://api.company-information.service.gov.uk/company/{test_company}"

print(f"\nMaking request to: {url}")
print(f"Using HTTP Basic Auth with API key as username")

try:
    response = requests.get(url, auth=(api_key, ''))

    print(f"\nResponse Status: {response.status_code}")

    if response.status_code == 200:
        print("\n" + "="*60)
        print("[SUCCESS] API Key is valid!")
        print("="*60)

        data = response.json()
        print(f"\nTest Company: {data.get('company_name')}")
        print(f"Company Number: {data.get('company_number')}")
        print(f"Status: {data.get('company_status')}")

        print("\n[OK] Your API key is working correctly")
        print("     You can now use the diagnostic scripts")

    elif response.status_code == 401:
        print("\n" + "="*60)
        print("[ERROR] API Key is INVALID")
        print("="*60)
        print("\nYour API key was rejected by Companies House.")
        print("\nPossible reasons:")
        print("  1. API key is incorrect or has typos")
        print("  2. API key has been revoked")
        print("  3. API key hasn't been activated yet")
        print("\nPlease:")
        print("  1. Check your .env file for typos")
        print("  2. Visit: https://developer.company-information.service.gov.uk/")
        print("  3. Log in and verify your API key")
        print("  4. Generate a new API key if needed")

    elif response.status_code == 429:
        print("\n[WARNING] Rate limit exceeded")
        print("Too many requests. Wait a few minutes and try again.")

    else:
        print(f"\n[ERROR] Unexpected response: {response.status_code}")
        print(f"Response: {response.text[:200]}")

except requests.exceptions.RequestException as e:
    print(f"\n[ERROR] Network error: {e}")
    print("\nPlease check:")
    print("  1. Internet connection")
    print("  2. Firewall/proxy settings")
    print("  3. Companies House API is accessible")

print("\n" + "="*60)

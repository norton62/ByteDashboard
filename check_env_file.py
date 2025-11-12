"""
Check .env file format and API key configuration.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("="*60)
print("Checking .env File Configuration")
print("="*60)

# Check if .env file exists
env_file = Path(".env")

if not env_file.exists():
    print("\n[ERROR] .env file not found!")
    print(f"Looking in: {Path.cwd()}")
    print("\nPlease create a .env file with:")
    print("COMPANIES_HOUSE_API_KEY=your_rest_api_key_here")
    exit(1)

print(f"\n[OK] .env file found at: {env_file.absolute()}")

# Read raw file contents
print("\n" + "="*60)
print("Raw .env File Contents:")
print("="*60)

with open(".env", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        # Show line with visible whitespace
        display_line = line.rstrip('\n')
        if 'COMPANIES_HOUSE_API_KEY' in display_line:
            # Mask the key for display
            if '=' in display_line:
                parts = display_line.split('=', 1)
                if len(parts[1]) > 8:
                    masked = parts[0] + '=' + parts[1][:8] + '...' + '*'*20
                    print(f"Line {i}: {masked}")
                else:
                    print(f"Line {i}: {display_line}")
            else:
                print(f"Line {i}: {display_line}")
        else:
            print(f"Line {i}: {display_line}")

# Load and check
print("\n" + "="*60)
print("After Loading with dotenv:")
print("="*60)

load_dotenv()
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")

if not api_key:
    print("\n[ERROR] COMPANIES_HOUSE_API_KEY not found after loading!")
    print("\nPossible issues:")
    print("  1. Key name is misspelled")
    print("  2. Line is commented out with #")
    print("  3. Wrong format")
    print("\nCorrect format:")
    print("COMPANIES_HOUSE_API_KEY=your_key_here")
    exit(1)

print(f"\n[OK] Key loaded successfully")
print(f"     Preview: {api_key[:8]}...{api_key[-4:]}")
print(f"     Length: {len(api_key)} characters")

# Check for common issues
issues = []

if api_key.startswith(' ') or api_key.endswith(' '):
    issues.append("Has leading or trailing spaces")

if api_key.startswith('"') or api_key.startswith("'"):
    issues.append("Wrapped in quotes (should not be)")

if '\n' in api_key or '\r' in api_key:
    issues.append("Contains newline characters")

if len(api_key) < 20:
    issues.append("Seems too short for an API key")

if issues:
    print("\n[WARNING] Potential Issues Detected:")
    for issue in issues:
        print(f"  - {issue}")
    print("\nRecommended format in .env file:")
    print("COMPANIES_HOUSE_API_KEY=583d17a6-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    print("                        ^no quotes, no spaces")
else:
    print("\n[OK] Key format looks good")

# Check key format (Companies House keys are typically UUIDs)
if '-' in api_key and len(api_key) == 36:
    print("\n[OK] Key matches UUID format (typical for Companies House)")
else:
    print("\n[INFO] Key format is non-standard")
    print("       Companies House REST API keys are usually 36-character UUIDs")
    print(f"       Your key is {len(api_key)} characters")

print("\n" + "="*60)
print("Testing with Companies House API...")
print("="*60)

import requests

# Test with a known company
test_url = "https://api.company-information.service.gov.uk/company/00000006"
print(f"\nRequest URL: {test_url}")
print(f"Auth Method: HTTP Basic (username=api_key, password='')")
print(f"Making request...")

try:
    response = requests.get(test_url, auth=(api_key, ''), timeout=10)

    print(f"Response Status: {response.status_code}")

    if response.status_code == 200:
        print("\n✓ [SUCCESS] API Key is VALID!")
        data = response.json()
        print(f"  Test Company: {data.get('company_name')}")
        print("\n  Your API key is working correctly!")

    elif response.status_code == 401:
        print("\n✗ [ERROR] API Key REJECTED (401 Unauthorized)")
        print("\n  This means:")
        print("  - The key format is being sent correctly")
        print("  - But Companies House doesn't recognize it as valid")
        print("\n  Please check:")
        print("  1. Copy the ENTIRE REST API key from Companies House developer portal")
        print("  2. Make sure you're using the REST API key (not Streaming API)")
        print("  3. Verify the key is still active in your Companies House account")
        print("  4. The key should look like: 583d17a6-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        print("\n  To get a fresh key:")
        print("  → https://developer.company-information.service.gov.uk/manage-applications")

    elif response.status_code == 429:
        print("\n⚠ [WARNING] Rate limit exceeded")
        print("  Wait a few minutes and try again")

    else:
        print(f"\n✗ [ERROR] Unexpected response: {response.status_code}")
        print(f"  Response body: {response.text[:200]}")

except requests.exceptions.Timeout:
    print("\n✗ [ERROR] Request timed out")
    print("  Check your internet connection")

except requests.exceptions.RequestException as e:
    print(f"\n✗ [ERROR] Network error: {e}")

print("\n" + "="*60)

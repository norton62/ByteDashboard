# Filing Deadlines from Companies House API

## Overview

The system now fetches filing deadlines directly from the Companies House API instead of relying solely on Excel data. This ensures you always have the most up-to-date deadline information.

## How It Works

### 1. Import Process

When importing companies from Excel:

**With API Key Configured:**
- System automatically fetches filing deadlines from Companies House API
- Excel deadline column is optional (but can be used as fallback)
- Each company's deadline is looked up individually
- Real-time, accurate deadline information

**Without API Key:**
- System uses Filing_Deadline column from Excel file
- Filing_Deadline column is required in this mode
- Manual deadline management

### 2. Refresh Deadlines

For existing companies in the database:
- Use the "📅 Refresh Deadlines" button on Client Management page
- Bulk updates all companies (or just filtered results)
- Updates deadlines from Companies House API
- Perfect for keeping deadlines current

## Excel File Format

### Minimal Format (API Mode)
Only two columns required when using API:

```
Company_Name          | Company_Number
---------------------|---------------
Tech Solutions Ltd   | 12345678
Green Energy Co      | 87654321
```

### Full Format (with Fallback)
Include deadline as fallback:

```
Company_Name          | Company_Number | Filing_Deadline
---------------------|----------------|----------------
Tech Solutions Ltd   | 12345678       | 2025-12-31
Green Energy Co      | 87654321       | 2026-03-15
```

## Setup Instructions

### 1. Get Companies House API Key

1. Visit: https://developer.company-information.service.gov.uk/
2. Register for an account
3. Create an application
4. Copy your API key

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
COMPANIES_HOUSE_API_KEY=your_api_key_here
```

Or set environment variable:

**Windows:**
```cmd
set COMPANIES_HOUSE_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export COMPANIES_HOUSE_API_KEY=your_api_key_here
```

### 3. Verify Configuration

On the main app page, check the "System Information" section:
- ✅ "Companies House API Key is configured" - API features enabled
- ⚠️ "Companies House API Key is not set" - Will use Excel deadlines

## Using API Features

### Initial Import with API Deadlines

1. Create Excel with just Company_Name and Company_Number
2. Run the application: `streamlit run app.py`
3. Click "Import Data from Excel"
4. System will show: "🔑 API Key detected - Will fetch filing deadlines from Companies House API"
5. Import process fetches deadline for each company automatically

**Console Output Example:**
```
Using Companies House API for filing deadlines
  Fetched deadline from API for 12345678: 2025-12-31
  Fetched deadline from API for 87654321: 2026-03-15
Imported 2 companies
```

### Refresh Existing Deadlines

On Client Management page:

1. Optionally search/filter to specific companies
2. Click "📅 Refresh Deadlines" button
3. System fetches current deadlines from API
4. Updates database with latest information

**Use Cases:**
- Regular deadline updates (monthly)
- After accounts are filed (deadline changes)
- When companies extend their filing deadline
- To verify deadline accuracy

### Check API Button

The "🔄 Check API" button:
- Checks filing STATUS (whether accounts are filed)
- Updates the "Accounts_Filed_CH" field
- Separate from deadline refresh

## API Rate Limits

Companies House API has rate limits:
- **600 requests per 5 minutes** per API key
- System processes companies sequentially
- Large batches (100+ companies) may take time
- Be patient with bulk operations

**Recommendations:**
- Process in batches if you have 500+ companies
- Use search/filter to refresh specific groups
- Schedule regular updates rather than constant checks

## Fallback Behavior

The system gracefully handles API failures:

1. **API Unavailable**: Falls back to Excel deadline
2. **Company Not Found**: Uses Excel deadline or skips
3. **No API Key**: Uses Excel deadline (required)
4. **Rate Limited**: Shows error, retry later

**Error Messages:**
```
API error for 12345678, using Excel deadline: HTTP 404
Skipping 99999999: No deadline available
Warning: API key not set, falling back to Excel deadlines
```

## Benefits

### Accuracy
- Always current deadline information
- Reflects any deadline extensions
- Automatic updates after filing

### Efficiency
- No manual deadline tracking
- Bulk refresh capability
- Simplified Excel files

### Compliance
- Real-time deadline monitoring
- Accurate overdue detection
- Reliable KPI calculations

## Troubleshooting

### "API Key Error" Messages

**Problem:** API key not found or invalid

**Solution:**
1. Check `.env` file exists and contains key
2. Verify no spaces around the key
3. Restart the application after setting key
4. Test key at Companies House developer portal

### Deadlines Not Updating

**Problem:** Refresh Deadlines button doesn't update

**Possible Causes:**
1. API rate limit exceeded - wait 5 minutes
2. Company number incorrect - verify format
3. Company not found at Companies House
4. Network connectivity issues

**Solution:**
- Check console for error messages
- Verify company numbers are correct (8 digits)
- Try smaller batch of companies
- Check network connection

### Import Fails with "No deadline available"

**Problem:** Company imported without deadline

**Causes:**
- API couldn't find company
- Company number incorrect
- No Filing_Deadline in Excel as fallback

**Solution:**
- Add Filing_Deadline column to Excel as fallback
- Verify company numbers are correct
- Check company exists at Companies House

## Best Practices

### Initial Setup
1. Configure API key before first import
2. Keep Filing_Deadline column in Excel as backup
3. Import in batches if you have 100+ companies

### Regular Maintenance
1. Refresh deadlines monthly
2. Use after filing accounts (deadline changes)
3. Check API button weekly for filing status
4. Export data regularly for backup

### Excel File Management
1. Keep minimal format (Name + Number only)
2. Let API provide deadlines
3. Add deadline column only if needed as backup
4. Use 8-digit company numbers (no leading zeros lost)

## Technical Details

### API Endpoints Used

**Company Profile:**
```
GET https://api.company-information.service.gov.uk/company/{company_number}
```

**Response Contains:**
- `accounts.next_due`: Next filing deadline
- `accounts.last_accounts.made_up_to`: Last filing date
- `accounts.overdue`: Boolean for overdue status

### Database Updates

New method: `update_filing_deadline()`
```python
db.update_filing_deadline(company_number, deadline)
```

Updates:
- Filing_Deadline field
- Last_Updated timestamp

### Import Process Flow

```
1. Read Excel file
2. Check if API key configured
3. For each company:
   a. Try fetch deadline from API
   b. If API fails, use Excel deadline
   c. If no deadline found, skip company
4. Import to database
5. Report results
```

## Examples

### Minimal Excel File
```python
import pandas as pd

data = {
    'Company_Name': ['Tech Ltd', 'Green Co'],
    'Company_Number': ['12345678', '87654321']
}

df = pd.DataFrame(data)
df.to_excel('clients.xlsx', index=False)
```

### Import with API
```python
from database import DatabaseManager

db = DatabaseManager()
count = db.import_from_excel('clients.xlsx', use_api_for_deadlines=True)
print(f"Imported {count} companies with API deadlines")
```

### Refresh Deadlines
```python
from api import CompaniesHouseAPI
from database import DatabaseManager

api = CompaniesHouseAPI()
db = DatabaseManager()

# Get all companies
companies = db.get_all_companies()
company_numbers = companies['Company_Number'].tolist()

# Fetch deadlines
results = api.bulk_get_filing_deadlines(company_numbers)

# Update database
for company_number, deadline in results.items():
    if deadline:
        db.update_filing_deadline(company_number, deadline)
```

---

**Summary:** The system now pulls filing deadlines from Companies House API automatically, ensuring accurate and up-to-date deadline information with minimal manual effort!

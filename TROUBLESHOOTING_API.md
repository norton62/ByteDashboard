# Troubleshooting: "No deadline available" Errors

## Issue

When refreshing deadlines from Companies House API, you see:
```
Skipping 12080057: No deadline available
Skipping 10487129: No deadline available
...
```

## Why This Happens

Companies House API doesn't provide deadline information for certain companies:

### Common Reasons:

1. **Company Status**
   - Dissolved companies
   - Companies in liquidation
   - Companies in administration
   - These companies no longer file accounts

2. **Company Type**
   - Certain company types are exempt from filing
   - Dormant companies (in some cases)
   - Overseas companies with no UK establishment

3. **Recently Incorporated**
   - New companies may not have their first deadline set yet
   - API data updates may be delayed

4. **API Data Availability**
   - Some companies simply don't have the `next_due` field in their API response
   - This is a Companies House data issue, not a bug in our system

## Diagnostic Steps

### Step 1: Run Quick Test

Test a specific problem company:

```bash
python quick_test_api.py
```

This will show you:
- Company name and status
- Whether the API response includes deadline information
- What fields are available in the accounts section

### Step 2: Run Full Diagnosis

For detailed analysis of all problem companies:

```bash
python diagnose_companies.py
```

This will check all 8 companies from your error list and show:
- Company details (name, status, type)
- Full accounts information
- Why deadline is unavailable
- Available alternative data

### Step 3: Check Manually

Visit Companies House website:
1. Go to: https://find-and-update.company-information.service.gov.uk/
2. Search for the company number (e.g., 12080057)
3. Check "Filing history" to see if company is active
4. Look at company status

## Solutions

### Option 1: Keep Excel Deadlines (Recommended)

For companies without API deadlines, keep the `Filing_Deadline` column in your Excel file:

```excel
Company_Name          | Company_Number | Filing_Deadline
---------------------|----------------|----------------
Active Company Ltd   | 12345678       |                 ← API will fill this
Dissolved Company    | 99999999       | 2025-12-31     ← Manual fallback
```

The import process uses this logic:
1. Try API first
2. If API fails, use Excel deadline
3. If both fail, skip the company

### Option 2: Filter Out Problem Companies

If these companies are no longer relevant:

1. Go to Client Management page
2. Search for each company number
3. Note which ones are dissolved/inactive
4. Remove them from your Excel file
5. Re-import

### Option 3: Manual Entry

For companies that need deadlines but API can't provide:

1. Look up deadline on Companies House website
2. Add to Excel with Filing_Deadline column
3. Import/re-import
4. Don't use "Refresh Deadlines" for these companies

## Understanding the Console Output

### Normal Skip (OK)
```
Skipping 12080057: No deadline available
```
**Meaning:** API couldn't find deadline. Company might be dissolved or exempt.

### With Verbose Mode
```
[12080057] Status: dissolved
[12080057] Company is dissolved - no deadline required
```
**Meaning:** Company is dissolved, so no deadline is needed. This is expected.

### API Error
```
Error fetching deadline for 12080057: HTTP 404
```
**Meaning:** Company not found. Check if company number is correct.

## Best Practices

### 1. Hybrid Approach
Use both API and Excel deadlines:

```excel
Company_Name     | Company_Number | Filing_Deadline
-----------------|----------------|----------------
New Company Ltd  | 12345678       |                 ← Let API fill
Old Company Ltd  | 99999999       | 2025-12-31     ← Manual for safety
```

- Active companies: Leave deadline blank, API will fetch
- Problem companies: Add manual deadline as backup

### 2. Regular Cleanup

Monthly:
1. Export your data
2. Review companies with no deadlines
3. Check status on Companies House website
4. Remove dissolved/inactive companies
5. Update Excel and re-import

### 3. Separate Active Companies

Create two Excel files:
- `clients_active.xlsx` - Only active companies (use API)
- `clients_manual.xlsx` - Problem companies (manual deadlines)

### 4. Document Problem Companies

Create a note file listing companies that don't work with API:

```
Problem Companies:
- 12080057: Dissolved 2024-01-15, keep for records
- 10487129: Dormant, manual deadline 2025-06-30
```

## Technical Details

### What the API Provides

Good response with deadline:
```json
{
  "accounts": {
    "next_due": "2025-12-31",
    "overdue": false
  }
}
```

Response without deadline:
```json
{
  "accounts": {
    "overdue": false
  }
}
```

No accounts section:
```json
{
  "company_status": "dissolved"
}
```

### System Behavior

When refreshing deadlines:
```
1. Fetch company profile from API
2. Check company_status
3. If dissolved/liquidated → Skip
4. Check accounts.next_due
5. If exists → Update database
6. If not exists → Skip (keep old deadline)
```

**Important:** Skipped companies keep their existing deadline in the database. The skip doesn't delete data, it just means "no update available."

## FAQ

**Q: Will these errors break my dashboard?**
A: No. Companies without API deadlines simply keep their existing deadline from the Excel import.

**Q: Should I manually add deadlines for skipped companies?**
A: Only if they're active companies you're still working with. Dissolved companies don't need deadlines.

**Q: Can I hide these skip messages?**
A: The messages are informational. They help you know which companies aren't being updated via API.

**Q: How do I know if a company is dissolved?**
A: Run `python diagnose_companies.py` and check the "Company Status" line.

**Q: Should I remove dissolved companies from my database?**
A: That depends on your record-keeping needs. If you want historical data, keep them. If not, remove them.

## Summary

**"No deadline available" is normal** for:
- Dissolved companies
- Companies in liquidation
- Some company types exempt from filing
- Recently incorporated companies

**What to do:**
1. Run diagnostic scripts to understand why
2. Keep Excel deadlines for problem companies
3. Remove dissolved companies if no longer needed
4. Use hybrid approach (API + Excel fallback)

**Not a bug!** The API simply doesn't provide deadline information for all companies.

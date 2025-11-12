# Feature: Automatic Filing Deadline Lookup

## Summary

Filing deadlines are now automatically fetched from the Companies House API instead of relying on manual Excel entry. This ensures always-current, accurate deadline information.

## What Changed

### 1. Excel File Simplification ✅
**Before:** Required 3 columns
- Company_Name
- Company_Number
- Filing_Deadline *(manual entry)*

**After:** Only 2 columns required (when using API)
- Company_Name
- Company_Number

Filing_Deadline is now *optional* and used only as a fallback!

### 2. Automatic Import with API ✅
**New Behavior:**
- On import, system checks for API key
- If found: Fetches deadline from Companies House for each company
- If not found: Uses Excel deadline column (required)
- Shows progress in console

### 3. Refresh Deadlines Button ✅
**New Feature:** "📅 Refresh Deadlines" button
- Located in Bulk Operations section
- Updates filing deadlines for all companies (or filtered results)
- Fetches latest deadline from Companies House API
- Perfect for regular updates

### 4. Smart Fallback ✅
- API lookup tries first
- Falls back to Excel if API fails
- Skips company if no deadline available
- Clear error messages

## Files Modified

### API Module (`api/companies_house.py`)
- Added `bulk_get_filing_deadlines()` method
- Fetches deadlines for multiple companies efficiently

### Database Module (`database/db_manager.py`)
- Updated `import_from_excel()` with `use_api_for_deadlines` parameter
- Added `update_filing_deadline()` method
- Smart fallback logic

### Client Management Page (`pages/2_📋_Client_Management.py`)
- Added "📅 Refresh Deadlines" button in Bulk Operations
- Re-Import now uses API automatically if key is configured
- Updated footer with deadline tip

### Main App (`app.py`)
- Import checks for API key presence
- Shows indicator if API will be used
- Automatic API import if configured

## How to Use

### Setup (One-Time)

1. **Get API Key:**
   - Visit: https://developer.company-information.service.gov.uk/
   - Register and create application
   - Copy API key

2. **Configure Environment:**
   ```bash
   # Create .env file
   echo "COMPANIES_HOUSE_API_KEY=your_key_here" > .env
   ```

3. **Verify:**
   - Run app: `streamlit run app.py`
   - Check System Information section
   - Should show: "✅ Companies House API Key is configured"

### Import with API Deadlines

**Option 1: Fresh Import**
1. Create minimal Excel (Name + Number only)
2. Run: `streamlit run app.py`
3. Click "Import Data from Excel"
4. System fetches deadlines automatically

**Option 2: Re-Import**
1. Go to Client Management page
2. Click "📤 Re-Import from Excel"
3. If API key configured, uses API automatically

### Refresh Existing Deadlines

1. Go to Client Management page
2. Optionally filter/search specific companies
3. Click "📅 Refresh Deadlines"
4. Deadlines update from API
5. Page refreshes with new data

## Benefits

✅ **Always Accurate** - Deadlines pulled from official source
✅ **No Manual Entry** - Eliminates typing errors
✅ **Automatic Updates** - One click to refresh all
✅ **Simpler Excel** - Just name and number needed
✅ **Deadline Extensions** - Automatically reflects changes
✅ **Smart Fallback** - Uses Excel if API unavailable

## Example Workflow

### Initial Setup
```bash
# 1. Set API key
echo "COMPANIES_HOUSE_API_KEY=abc123..." > .env

# 2. Create minimal Excel
python generate_simple_template.py

# 3. Add your company numbers to clients_template.xlsx

# 4. Rename to clients.xlsx

# 5. Run app and import
streamlit run app.py
```

### Monthly Maintenance
```
1. Open Client Management page
2. Click "📅 Refresh Deadlines"
3. All deadlines updated from API
4. Review any changes
```

### After Filing Accounts
```
1. Search for the company
2. Click "🔄 Check API" (updates filed status)
3. Click "📅 Refresh Deadlines" (updates next deadline)
4. Both fields now current
```

## Technical Details

### API Call Example
```python
# Fetch deadline for one company
deadline = api.get_filing_deadline('12345678')
# Returns: '2025-12-31'

# Bulk fetch for multiple companies
results = api.bulk_get_filing_deadlines(['12345678', '87654321'])
# Returns: {'12345678': '2025-12-31', '87654321': '2026-03-15'}
```

### Database Update
```python
# Update deadline in database
db.update_filing_deadline('12345678', '2025-12-31')
# Also updates Last_Updated timestamp
```

### Import with API
```python
# Import with API deadlines
count = db.import_from_excel('clients.xlsx', use_api_for_deadlines=True)
# Automatically fetches from API for each company
```

## Rate Limits

**Companies House API:**
- 600 requests per 5 minutes
- System processes sequentially
- Large imports (100+ companies) take time

**Recommendations:**
- Be patient with bulk operations
- Use filters for targeted updates
- Schedule regular refreshes (not constant)

## Error Handling

All API operations have graceful fallbacks:

```
✅ API Success: Uses API deadline
⚠️ API Fails: Falls back to Excel deadline
❌ Both Fail: Skips company, logs error
```

**Console Output:**
```
Using Companies House API for filing deadlines
  Fetched deadline from API for 12345678: 2025-12-31
  API error for 99999999, using Excel deadline: HTTP 404
  Skipping 88888888: No deadline available
Imported 2 companies
```

## Future Enhancements

Potential additions:
- [ ] Progress bar for bulk API operations
- [ ] Schedule automatic daily/weekly refreshes
- [ ] Deadline change notifications
- [ ] Batch processing for large datasets
- [ ] Cache API results to reduce calls

## Documentation

See `API_DEADLINES.md` for comprehensive documentation including:
- Detailed setup instructions
- Troubleshooting guide
- Best practices
- API technical details
- Code examples

---

**Result:** Filing deadlines are now automatically managed via the Companies House API, ensuring accuracy and reducing manual work!

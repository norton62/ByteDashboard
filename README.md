# Company Accounts Dashboard

A secure, professional Python web application built with Streamlit to manage and monitor company accounts filing statuses. This dashboard integrates with the Companies House API to track filing deadlines, internal workflow statuses, and provide real-time KPI monitoring.

## Features

### Dashboard View (TV Mode)
- Large, easy-to-read indicators perfect for TV displays
- 4 Key Performance Indicators:
  - **Accounts Outstanding**: Companies with deadlines ≤ 31/07/2026 not yet filed
  - **Ready to Submit**: Companies ready for submission
  - **Sent to Client**: Accounts sent to clients for review
  - **Missing Information**: Companies requiring additional information
- Auto-refresh capability for continuous monitoring
- Clean, professional design optimized for readability

### Client Management
- **Searchable Table**: Quick search by company name or number
- **Sortable Columns**: Sort by name, deadline, or status
- **Editable Status**: Update internal workflow statuses
- **Companies House Integration**: Bulk check filing statuses via API
- **Data Export**: Export filtered data to Excel
- **Bulk Import**: Re-import data from Excel

### Data Management
- **SQLite Database**: Local persistent storage in `client_data.db`
- **Excel Import**: Initial data loading from `clients.xlsx`
- **Automatic Timestamps**: Track when records were last updated
- **Data Integrity**: Primary key constraints and validation

## Technology Stack

- **Python**: 3.10+
- **Web Framework**: Streamlit
- **Database**: SQLite3
- **Data Processing**: Pandas
- **API Integration**: Requests
- **Excel Support**: OpenPyXL

## Project Structure

```
ByteDashboard/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── clients.xlsx                    # Initial data import file
├── client_data.db                  # SQLite database (created on first run)
├── .env.example                    # Environment variables template
├── generate_dummy_data.py          # Script to generate sample data
├── README.md                       # This file
│
├── database/
│   ├── __init__.py
│   └── db_manager.py              # Database operations and schema
│
├── api/
│   ├── __init__.py
│   └── companies_house.py         # Companies House API integration
│
└── pages/
    ├── 1_📊_Dashboard.py          # Dashboard view (TV mode)
    └── 2_📋_Client_Management.py  # Client management interface
```

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Companies House API key (optional, for API features)

### Step 1: Clone or Download

```bash
cd ByteDashboard
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Generate Sample Data (Optional)

If you don't have a `clients.xlsx` file, generate sample data:

```bash
python generate_dummy_data.py
```

This creates a `clients.xlsx` file with 20 dummy companies.

### Step 4: Configure Environment Variables (Optional)

For Companies House API integration:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   COMPANIES_HOUSE_API_KEY=your_actual_api_key_here
   ```

3. Get an API key from: https://developer.company-information.service.gov.uk/

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Initial Data Import

### Excel File Format

Your `clients.xlsx` file must contain these columns:

| Column Name      | Type   | Description                          | Example        |
|------------------|--------|--------------------------------------|----------------|
| Company_Name     | Text   | Name of the company                  | Tech Ltd       |
| Company_Number   | Text   | Company registration number (8 digits)| 12345001       |
| Filing_Deadline  | Date   | Accounts filing deadline             | 2026-07-31     |

### Import Process

1. Ensure `clients.xlsx` is in the project root directory
2. Open the application: `streamlit run app.py`
3. Click "Import Data from Excel" on the home page
4. The system will import all companies into the database

**Note**: Re-importing will only add NEW companies (based on Company_Number). Existing companies are not updated.

## Usage Guide

### Home Page

- View overall statistics and KPIs
- Check system configuration
- Import initial data
- Navigate to Dashboard or Client Management

### Dashboard Page (📊)

**Purpose**: Large-screen monitoring (ideal for TV displays)

**Features**:
- Large, readable KPI indicators
- Overall statistics
- Manual refresh button
- Clean, distraction-free interface

**Use Case**: Display on office TV for team visibility

### Client Management Page (📋)

**Purpose**: Day-to-day management of company accounts

**Features**:

1. **Search & Filter**
   - Search by company name or number
   - Sort by deadline, name, or status
   - Ascending/descending order

2. **View Company Data**
   - See all companies in a table
   - View filing deadlines
   - Check filing status from Companies House
   - See last update timestamps

3. **Edit Status**
   - Select a company
   - Choose new status from dropdown:
     - Not Started
     - Started
     - Sent to Client
     - Missing Information
     - Ready to Submit
   - Click "Update Status" to save

4. **Companies House API**
   - Click "Check All Filing Statuses" to bulk-check all visible companies
   - Updates `Accounts_Filed_CH` field automatically
   - Requires API key to be configured

5. **Bulk Operations**
   - Export current view to Excel
   - Re-import data from `clients.xlsx`

## Database Schema

### companies Table

| Column           | Type      | Description                              |
|------------------|-----------|------------------------------------------|
| Company_Number   | TEXT (PK) | Unique company registration number       |
| Company_Name     | TEXT      | Company name                             |
| Filing_Deadline  | DATE      | Accounts filing deadline                 |
| Internal_Status  | TEXT      | Workflow status (default: 'Not Started') |
| Accounts_Filed_CH| BOOLEAN   | Filed status from Companies House API    |
| Last_Updated     | TIMESTAMP | Last modification timestamp              |

## API Integration

### Companies House API

The application integrates with the Companies House API to automatically check filing statuses.

**Setup**:
1. Register at https://developer.company-information.service.gov.uk/
2. Get your API key
3. Set environment variable: `COMPANIES_HOUSE_API_KEY`

**Usage**:
- Go to Client Management page
- Click "Check All Filing Statuses"
- System queries Companies House for each company
- Updates `Accounts_Filed_CH` field automatically

**API Endpoints Used**:
- `GET /company/{company_number}` - Retrieve company profile and filing information

**Rate Limiting**: Companies House API has rate limits. For large datasets, bulk checking may take time.

## Security Considerations

### API Key Storage
- **Never** commit `.env` file to version control
- Use environment variables for sensitive data
- The `.env.example` file is provided as a template only

### Database Security
- Database file (`client_data.db`) contains company information
- Store in a secure location
- Consider access controls for production deployments
- Regular backups recommended

### Input Validation
- All database inputs are parameterized to prevent SQL injection
- Status updates are validated against allowed values
- Company numbers and names are sanitized

## Troubleshooting

### Application won't start

**Error**: `ModuleNotFoundError`
- **Solution**: Run `pip install -r requirements.txt`

**Error**: `No such file or directory: 'clients.xlsx'`
- **Solution**: Run `python generate_dummy_data.py` or create your own Excel file

### Database issues

**Error**: `Database is locked`
- **Solution**: Close any other applications accessing `client_data.db`

**Problem**: Data not persisting
- **Solution**: Ensure `client_data.db` is not read-only

### API integration issues

**Error**: `COMPANIES_HOUSE_API_KEY environment variable`
- **Solution**: Set the environment variable or create `.env` file

**Error**: `HTTP 401 Unauthorized`
- **Solution**: Check your API key is valid and active

**Error**: `HTTP 429 Too Many Requests`
- **Solution**: You've hit the rate limit. Wait and try again later

### UI issues

**Problem**: Dashboard looks cramped
- **Solution**: Use full-screen mode (F11) or increase browser zoom

**Problem**: Tables not displaying correctly
- **Solution**: Clear browser cache and reload

## Maintenance

### Backup Database

```bash
# Create a backup
cp client_data.db client_data.backup.db

# Or with timestamp
cp client_data.db "client_data_$(date +%Y%m%d).db"
```

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Clear Database (Start Fresh)

```bash
# Delete the database file
rm client_data.db

# Restart the application - it will create a new database
streamlit run app.py
```

## Customization

### Modify KPI Deadline

The default deadline cutoff is 31/07/2026. To change:

Edit `database/db_manager.py:216`:
```python
def get_kpi_counts(self, deadline_cutoff: str = "2026-07-31") -> Dict[str, int]:
```

Change the default value to your desired date.

### Add New Status Options

Edit `pages/2_📋_Client_Management.py:58`:
```python
STATUS_OPTIONS = [
    'Not Started',
    'Started',
    'Sent to Client',
    'Missing Information',
    'Ready to Submit',
    'Your New Status'  # Add here
]
```

Also update validation in `database/db_manager.py:145`.

### Customize Dashboard Colors

Edit the CSS in `pages/1_📊_Dashboard.py:20` to change colors and styling.

## Development

### Project Requirements

- Maintain Python 3.10+ compatibility
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Write unit tests for new features

### Adding New Pages

1. Create file in `pages/` directory: `3_Your_Page.py`
2. Use emoji prefix for icon in sidebar
3. Import necessary modules
4. Follow existing page structure

### Extending Database

1. Add migration function in `db_manager.py`
2. Update schema in `initialize_database()`
3. Add corresponding CRUD operations
4. Update relevant pages to use new fields

## Support & Resources

- **Streamlit Documentation**: https://docs.streamlit.io/
- **Companies House API Docs**: https://developer.company-information.service.gov.uk/
- **Python SQLite3 Docs**: https://docs.python.org/3/library/sqlite3.html
- **Pandas Documentation**: https://pandas.pydata.org/docs/

## License

This project is provided as-is for internal business use.

## Version History

### v1.0 (Current)
- Initial release
- Dashboard and Client Management pages
- SQLite database integration
- Companies House API integration
- Excel import/export functionality
- Search, sort, and filter capabilities

---

**Built with ❤️ using Python and Streamlit**

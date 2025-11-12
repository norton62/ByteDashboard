# Quick Start Guide

## Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```

### 3. Import Your Data
- The application will open in your browser at `http://localhost:8501`
- Click "Import Data from Excel" on the home page
- Your data from `clients.xlsx` will be imported

## That's It!

You can now:
- View the **Dashboard** page for TV display
- Manage companies in the **Client Management** page
- Update statuses, search, and filter companies

## Optional: Enable API Integration

1. Get an API key from https://developer.company-information.service.gov.uk/
2. Create a `.env` file:
   ```
   COMPANIES_HOUSE_API_KEY=your_api_key_here
   ```
3. Restart the application

## Need Help?

- See `README.md` for detailed documentation
- Check the application's home page for system information
- View the built-in help tooltips in the UI

---

**Pro Tip**: The Dashboard page is perfect for displaying on a TV or large monitor for team visibility!

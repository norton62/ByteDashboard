"""
Company Accounts Dashboard - Main Application
A Streamlit-based web application for managing company accounts filing statuses.
"""
import streamlit as st
from pathlib import Path
from database import DatabaseManager
import os
from dotenv import load_dotenv
from auth import check_password

# Load environment variables from .env file
load_dotenv()

# Check authentication
if not check_password():
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Company Accounts Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Force light mode text */
    .main .block-container {
        color: #262730 !important;
    }

    /* All text elements */
    p, li, span, div, h1, h2, h3, h4, h5, h6 {
        color: #262730 !important;
    }

    /* Main page styling */
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-radius: 10px;
        margin-bottom: 30px;
    }

    .main-header h1 {
        color: white !important;
    }

    .main-header p {
        color: white !important;
    }

    .feature-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        color: #262730 !important;
    }

    .feature-card h3 {
        color: #262730 !important;
    }

    .feature-card p, .feature-card ul, .feature-card li {
        color: #262730 !important;
    }

    .setup-step {
        background-color: #e7f3ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #2196F3;
        color: #0d47a1 !important;
    }

    .setup-step h3 {
        color: #0d47a1 !important;
    }

    .setup-step p, .setup-step ul, .setup-step li {
        color: #0d47a1 !important;
    }

    /* Fix metric labels and values */
    [data-testid="stMetricValue"] {
        color: #0e1117 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #262730 !important;
    }

    /* Button styling */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        padding: 10px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_db():
    """Get database manager instance and initialize if needed."""
    db = DatabaseManager()
    return db

db = get_db()

# Main header
st.markdown("""
    <div class="main-header">
        <h1>🏢 Company Accounts Dashboard</h1>
        <p style="font-size: 18px; margin-top: 10px;">
            Manage and monitor company accounts filing statuses
        </p>
    </div>
""", unsafe_allow_html=True)

# Check if database has data
stats = db.get_database_stats()

if stats['total_companies'] == 0:
    # First-time setup
    st.warning("⚠️ No data found in database. Please complete the initial setup.")

    st.markdown("## 🚀 Initial Setup")

    st.markdown("""
    <div class="setup-step">
        <h3>Step 1: Verify Excel File</h3>
        <p>Make sure <code>clients.xlsx</code> exists in the project directory with the following columns:</p>
        <ul>
            <li><strong>Company_Name</strong>: Name of the company</li>
            <li><strong>Company_Number</strong>: Company registration number</li>
            <li><strong>Filing_Deadline</strong>: Filing deadline date (YYYY-MM-DD format)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Check if Excel file exists
    excel_file = Path("clients.xlsx")
    if excel_file.exists():
        st.success("✅ clients.xlsx found!")

        st.markdown("""
        <div class="setup-step">
            <h3>Step 2: Import Data</h3>
            <p>Click the button below to import company data from the Excel file into the database.</p>
        </div>
        """, unsafe_allow_html=True)

        # Check if API key is available
        api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
        if api_key:
            st.info("🔑 API Key detected - Will fetch filing deadlines from Companies House API")
            use_api_import = True
        else:
            st.warning("⚠️ No API Key - Will use filing deadlines from Excel file")
            use_api_import = False

        if st.button("📥 Import Data from Excel", width='stretch', type="primary"):
            try:
                if use_api_import:
                    with st.spinner("Importing data and fetching deadlines from API..."):
                        count = db.import_from_excel(str(excel_file), use_api_for_deadlines=True)
                else:
                    with st.spinner("Importing data..."):
                        count = db.import_from_excel(str(excel_file), use_api_for_deadlines=False)
                st.success(f"✅ Successfully imported {count} companies!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error importing data: {e}")
    else:
        st.error(f"❌ clients.xlsx not found in {Path.cwd()}")
        st.info("💡 Run `python generate_dummy_data.py` to create a sample Excel file.")

    st.markdown("""
    <div class="setup-step">
        <h3>Step 3: Configure API (Optional)</h3>
        <p>To enable Companies House API integration, set the environment variable:</p>
        <code>COMPANIES_HOUSE_API_KEY=your_api_key_here</code>
        <p style="margin-top: 10px;">You can get an API key from <a href="https://developer.company-information.service.gov.uk/" target="_blank">Companies House Developer Hub</a></p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Dashboard overview
    st.markdown("## 📊 Dashboard Overview")

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)

    kpis = db.get_kpi_counts()

    with col1:
        st.metric(
            label="⏰ Outstanding",
            value=kpis['outstanding'],
            help="Accounts with deadlines ≤ 31/07/2026 not yet filed"
        )

    with col2:
        st.metric(
            label="✅ Ready to Submit",
            value=kpis['ready']
        )

    with col3:
        st.metric(
            label="📤 Sent to Client",
            value=kpis['sent']
        )

    with col4:
        st.metric(
            label="❗ Missing Info",
            value=kpis['missing']
        )

    # Quick stats
    st.markdown("---")
    st.markdown("## 📈 Quick Statistics")

    col_stat1, col_stat2, col_stat3 = st.columns(3)

    with col_stat1:
        st.metric("Total Companies", stats['total_companies'])

    with col_stat2:
        st.metric("Accounts Filed", stats['filed_count'])

    with col_stat3:
        st.metric("Accounts Not Filed", stats['unfiled_count'])

    # Navigation guide
    st.markdown("---")
    st.markdown("## 🧭 Navigation")

    col_nav1, col_nav2 = st.columns(2)

    with col_nav1:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Dashboard</h3>
            <p>Large, TV-friendly view showing key performance indicators.</p>
            <ul>
                <li>Accounts Outstanding</li>
                <li>Ready to Submit</li>
                <li>Sent to Client</li>
                <li>Missing Information</li>
            </ul>
            <p><strong>Best for:</strong> Monitoring at a glance, TV display</p>
        </div>
        """, unsafe_allow_html=True)

    with col_nav2:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Client Management</h3>
            <p>Detailed table view for managing company accounts.</p>
            <ul>
                <li>Search and filter companies</li>
                <li>Sort by deadline, name, or status</li>
                <li>Edit company statuses</li>
                <li>Check Companies House API</li>
            </ul>
            <p><strong>Best for:</strong> Day-to-day management</p>
        </div>
        """, unsafe_allow_html=True)

# Features section
st.markdown("---")
st.markdown("## ✨ Features")

col_feat1, col_feat2, col_feat3 = st.columns(3)

with col_feat1:
    st.markdown("""
    ### 🔍 Search & Filter
    - Quick search by company name or number
    - Sort by multiple criteria
    - Filter by status and deadlines
    """)

with col_feat2:
    st.markdown("""
    ### ✏️ Easy Editing
    - Update company statuses
    - Track internal workflow stages
    - Automatic timestamp tracking
    """)

with col_feat3:
    st.markdown("""
    ### 🔄 API Integration
    - Check Companies House filing status
    - Bulk status updates
    - Real-time data synchronization
    """)

# System information
st.markdown("---")
st.markdown("## ℹ️ System Information")

with st.expander("📂 Database Information"):
    st.write(f"**Database Path:** {Path('client_data.db').absolute()}")
    st.write(f"**Total Companies:** {stats['total_companies']}")
    st.write(f"**Database Size:** {Path('client_data.db').stat().st_size / 1024:.2f} KB" if Path('client_data.db').exists() else "N/A")

with st.expander("🔑 API Configuration"):
    api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
    if api_key:
        st.success("✅ Companies House API Key is configured")
        st.write(f"**Key Preview:** {api_key[:8]}...")
    else:
        st.warning("⚠️ Companies House API Key is not set")
        st.info("Set the COMPANIES_HOUSE_API_KEY environment variable to enable API features")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Company Accounts Dashboard v1.0</p>
        <p>Built with Streamlit 🎈 | Python 🐍 | SQLite 💾</p>
    </div>
""", unsafe_allow_html=True)

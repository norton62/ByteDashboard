"""
Dashboard Page - TV View
Large indicators showing key performance metrics for company accounts filing.
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import time

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database import DatabaseManager
from api import CompaniesHouseAPI
from auth import check_password

# Check authentication
if not check_password():
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful TV-friendly display
st.markdown("""
    <style>
    /* Hide sidebar on this page for TV view */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Clean light background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
    }

    /* Ensure all text is dark */
    .main .block-container {
        background-color: transparent !important;
        color: #262730 !important;
    }

    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    /* Force default text to be dark */
    p, li, span, h1, h2, h3, h4, h5, h6, label, strong {
        color: #262730 !important;
    }

    /* Hero title */
    .dashboard-title {
        text-align: center;
        color: #1a237e !important;
        font-size: 64px;
        font-weight: 800;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .dashboard-subtitle {
        text-align: center;
        color: #666 !important;
        font-size: 24px;
        margin-bottom: 20px;
        font-weight: 300;
    }

    /* Big Metric Cards */
    .big-metric-card {
        background: white;
        padding: 50px 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
        transition: all 0.3s ease;
        border: 3px solid;
        margin: 10px 0;
    }

    .big-metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 60px rgba(0, 0, 0, 0.2);
    }

    .card-purple {
        border-color: #667eea;
        background: linear-gradient(135deg, #ffffff 0%, #f5f7ff 100%);
    }

    .card-yellow {
        border-color: #f6b93b;
        background: linear-gradient(135deg, #ffffff 0%, #fffbf0 100%);
    }

    .card-blue {
        border-color: #4a90e2;
        background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
    }

    .card-red {
        border-color: #e74c3c;
        background: linear-gradient(135deg, #ffffff 0%, #fff5f5 100%);
    }

    .metric-icon {
        font-size: 80px;
        margin-bottom: 20px;
        line-height: 1;
    }

    .metric-value {
        font-size: 96px;
        font-weight: 900;
        color: #1a237e;
        margin: 20px 0;
        line-height: 1;
    }

    .metric-label {
        font-size: 22px;
        font-weight: 600;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 15px;
    }

    /* Status cards */
    .status-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }

    .status-card h3 {
        color: #1a237e;
        margin-bottom: 15px;
        font-size: 20px;
    }

    .status-item {
        display: flex;
        justify-content: space-between;
        padding: 12px;
        margin: 8px 0;
        border-radius: 10px;
        font-size: 16px;
    }

    .status-not-started {
        background-color: #f5f5f5;
        color: #424242;
    }

    .status-started {
        background-color: #fff3cd;
        color: #856404;
    }

    .status-sent {
        background-color: #cce5ff;
        color: #004085;
    }

    .status-missing {
        background-color: #f8d7da;
        color: #721c24;
    }

    .status-ready {
        background-color: #d4edda;
        color: #155724;
    }

    /* Time display */
    .time-display {
        text-align: center;
        color: #1a237e !important;
        font-size: 72px;
        font-weight: 700;
        margin-top: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .date-display {
        text-align: center;
        color: #666 !important;
        font-size: 28px;
        margin-bottom: 50px;
        font-weight: 300;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_db():
    """Get database manager instance."""
    return DatabaseManager()

db = get_db()

# Auto-update filing deadlines every hour
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None

now = datetime.now()

# Check if we need to update (first run or 1 hour has passed)
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
if api_key:
    should_update = False

    if st.session_state.last_update_time is None:
        should_update = True
    elif (now - st.session_state.last_update_time) >= timedelta(hours=1):
        should_update = True

    if should_update:
        try:
            api = CompaniesHouseAPI()
            all_companies = db.get_all_companies()

            if not all_companies.empty:
                company_numbers = all_companies['Company_Number'].tolist()

                # Update deadlines in background
                results = api.bulk_get_filing_deadlines(company_numbers)
                updated_count = 0

                for company_number, deadline in results.items():
                    if deadline:
                        db.update_filing_deadline(company_number, deadline)
                        updated_count += 1

                st.session_state.last_update_time = now

        except Exception as e:
            # Silently fail - don't disrupt the dashboard
            pass

# Header with time
st.markdown(f'<div class="time-display">{now.strftime("%H:%M")}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="date-display">{now.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)

# Title
st.markdown('<div class="dashboard-title">📊 Operation Lock In</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Tracker of Progress</div>', unsafe_allow_html=True)

# Get KPI data
all_df = db.get_all_companies()

# Calculate metrics
deadline_count = all_df[all_df['Filing_Deadline'] <= '2026-07-31'].shape[0]

if not all_df.empty:
    status_counts = all_df['Internal_Status'].value_counts()
    started_count = status_counts.get('Started', 0)
    sent_count = status_counts.get('Sent to Client', 0)
    missing_count = status_counts.get('Missing Information', 0)
else:
    started_count = 0
    sent_count = 0
    missing_count = 0

# Add spacing
st.markdown("<br><br>", unsafe_allow_html=True)

# Create 4 big metric cards
col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    st.markdown(f"""
        <div class="big-metric-card card-purple">
            <div class="metric-icon">📅</div>
            <div class="metric-value">{deadline_count}</div>
            <div class="metric-label">Deadline ≤ 31/07/26</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="big-metric-card card-yellow">
            <div class="metric-icon">🔨</div>
            <div class="metric-value">{started_count}</div>
            <div class="metric-label">Started</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="big-metric-card card-blue">
            <div class="metric-icon">📤</div>
            <div class="metric-value">{sent_count}</div>
            <div class="metric-label">Sent to Client</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="big-metric-card card-red">
            <div class="metric-icon">⚠️</div>
            <div class="metric-value">{missing_count}</div>
            <div class="metric-label">Missing Information</div>
        </div>
    """, unsafe_allow_html=True)

# Footer with last update time
st.markdown("<br><br>", unsafe_allow_html=True)
if st.session_state.last_update_time:
    last_update_str = st.session_state.last_update_time.strftime("%H:%M on %d/%m/%Y")
    st.markdown(f"""
        <div style="text-align: center; color: #999; font-size: 14px; margin-top: 40px;">
            📡 Last API sync: {last_update_str} | Next sync: {(st.session_state.last_update_time + timedelta(hours=1)).strftime("%H:%M")}
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="text-align: center; color: #999; font-size: 14px; margin-top: 40px;">
            📡 Automatic hourly sync enabled
        </div>
    """, unsafe_allow_html=True)

# Auto-refresh page every 5 minutes to check for updates
st.markdown("""
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 300000); // 5 minutes in milliseconds
    </script>
""", unsafe_allow_html=True)

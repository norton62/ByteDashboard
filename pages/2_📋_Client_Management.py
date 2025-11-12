"""
Client Management Page
Searchable, sortable, and editable table for managing company accounts.
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

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
    page_title="Client Management",
    page_icon="📋",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    /* Force light mode with dark text */
    .main .block-container {
        background-color: #ffffff !important;
        color: #262730 !important;
    }

    /* Ensure all text is dark */
    p, li, span, div, h1, h2, h3, h4, h5, h6, label {
        color: #262730 !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }

    /* Align all input controls */
    .stTextInput > label,
    .stSelectbox > label {
        font-size: 14px !important;
        font-weight: 400 !important;
        margin-bottom: 0.5rem !important;
        height: 1.5rem !important;
    }

    /* Text input styling */
    .stTextInput > div > div > input {
        min-height: 36px !important;
        max-height: 36px !important;
        padding: 0px 12px !important;
        font-size: 14px !important;
    }

    /* Compact dropdowns */
    .stSelectbox [data-baseweb="select"] {
        min-height: 36px !important;
        max-height: 36px !important;
        width: 100% !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        min-height: 36px !important;
        max-height: 36px !important;
        padding: 0px 8px !important;
        font-size: 13px !important;
        line-height: 36px !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Reduce selectbox container spacing */
    .stSelectbox {
        margin-bottom: 0px !important;
    }

    /* Align button with inputs */
    .stButton {
        margin-top: 1.95rem !important;
    }

    /* Make dropdown menu text readable */
    [role="listbox"] [role="option"] {
        font-size: 13px !important;
        padding: 6px 12px !important;
    }

    /* Fix metric styling */
    [data-testid="stMetricValue"] {
        color: #0e1117 !important;
        font-size: 32px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #262730 !important;
        font-size: 14px !important;
    }

    /* Column headers */
    .column-header {
        font-weight: 700;
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 8px;
    }

    /* Company name display */
    .company-name-text {
        font-size: 14px;
        font-weight: 600;
        color: #1a237e;
    }

    .company-number-text {
        font-size: 11px;
        color: #999;
        margin-left: 6px;
    }

    /* Overdue text */
    .overdue-text {
        color: #d32f2f;
        font-weight: bold;
    }

    /* Make wrapper divs contain their children properly */
    .stMarkdown > div > div {
        width: 100% !important;
    }

    /* Ensure horizontal blocks inside wrappers are full width */
    div[data-testid="stHorizontalBlock"] {
        background-color: transparent !important;
    }

    /* Make columns transparent so parent background shows */
    div[data-testid="column"] {
        background-color: transparent !important;
    }

    /* Make all elements inside transparent */
    .element-container {
        background-color: transparent !important;
    }

    /* Minimal row spacing */
    .element-container {
        margin-bottom: 0px !important;
        padding-bottom: 3px !important;
    }

    /* Small gap between company rows */
    div[data-testid="stHorizontalBlock"] {
        margin-bottom: 8px !important;
        gap: 0rem !important;
    }

    /* Small column padding */
    [data-testid="column"] {
        padding-top: 3px !important;
        padding-bottom: 3px !important;
    }

    /* HR styling - small margin */
    hr {
        margin: 3px 0 !important;
        padding: 0px !important;
    }

    /* Minimal vertical block gaps */
    div[data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        gap: 0rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_db():
    return DatabaseManager()

db = get_db()

# Status options
STATUS_OPTIONS = [
    'Not Started',
    'Started',
    'Sent to Client',
    'Missing Information',
    'Ready to Submit'
]

# Title
st.title("📋 Client Management")

# Top metrics
col_stat1, col_stat2, col_stat3 = st.columns(3)
all_df = db.get_all_companies()

with col_stat1:
    st.metric("Total Companies", len(all_df))

with col_stat2:
    deadline_count = all_df[all_df['Filing_Deadline'] <= '2026-07-31'].shape[0]
    st.metric("Deadline ≤ 31/07/2026", deadline_count)

with col_stat3:
    overdue_count = all_df[
        (all_df['Filing_Deadline'] < datetime.now().strftime("%Y-%m-%d"))
    ].shape[0]
    st.metric("⚠️ Overdue", overdue_count)

st.markdown("---")

# Search and filter controls - all aligned
col_search, col_sort, col_order, col_api = st.columns([3, 1.5, 1, 1.5])

with col_search:
    search_term = st.text_input(
        "Search",
        placeholder="Company name or number...",
        key="search_box"
    )

with col_sort:
    sort_by = st.selectbox(
        "Sort By",
        options=["Filing_Deadline", "Company_Name", "Internal_Status"],
        index=0
    )

with col_order:
    sort_order = st.selectbox(
        "Order",
        options=["Ascending", "Descending"],
        index=0
    )

with col_api:
    if st.button("🔄 Sync API", width='stretch', help="Update from Companies House"):
        try:
            api = CompaniesHouseAPI()
            api_df = db.search_companies(search_term) if search_term else db.get_all_companies()
            company_numbers = api_df['Company_Number'].tolist()

            with st.spinner(f"Updating {len(company_numbers)} companies..."):
                results = api.bulk_get_filing_deadlines(company_numbers)
                updated_count = sum(1 for d in results.values() if d)

                for company_number, deadline in results.items():
                    if deadline:
                        db.update_filing_deadline(company_number, deadline)

                st.success(f"✅ Updated {updated_count}")
                st.rerun()

        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ {e}")

# Get and sort data
if search_term:
    df = db.search_companies(search_term)
else:
    df = db.get_all_companies()

ascending = sort_order == "Ascending"
if not df.empty:
    df = df.sort_values(by=sort_by, ascending=ascending)

st.markdown("---")

# Company list with headers
st.subheader(f"📊 Companies ({len(df)})")

if df.empty:
    st.warning("No companies found.")
else:
    # Column headers
    h1, h2, h3, h4 = st.columns([3, 1.5, 1.3, 2.5])

    with h1:
        st.markdown('<div class="column-header">Company</div>', unsafe_allow_html=True)
    with h2:
        st.markdown('<div class="column-header">Deadline</div>', unsafe_allow_html=True)
    with h3:
        st.markdown('<div class="column-header">Days Left</div>', unsafe_allow_html=True)
    with h4:
        st.markdown('<div class="column-header">Status</div>', unsafe_allow_html=True)

    # Company rows
    for idx, row in df.iterrows():
        # Determine status colors
        status = row['Internal_Status']
        status_colors = {
            'Not Started': ('#f5f5f5', '#9e9e9e'),
            'Started': ('#fff9e6', '#f6b93b'),
            'Sent to Client': ('#e3f2fd', '#4a90e2'),
            'Missing Information': ('#ffebee', '#e74c3c'),
            'Ready to Submit': ('#e8f5e9', '#4caf50')
        }
        bg_color, border_color = status_colors.get(status, ('#f5f5f5', '#9e9e9e'))

        col1, col2, col3, col4 = st.columns([3, 1.5, 1.3, 2.5])

        # Add custom CSS to style this specific row
        st.markdown(f"""
            <style>
            div[data-testid="column"]:has(span.company-id-{row['Company_Number']}) {{
                background-color: {bg_color} !important;
            }}
            div[data-testid="stHorizontalBlock"]:has(span.company-id-{row['Company_Number']}) {{
                background-color: {bg_color} !important;
                border-left: 4px solid {border_color} !important;
                padding: 8px !important;
                margin: 4px 0 !important;
                border-radius: 6px !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        is_overdue = row['Filing_Deadline'] < datetime.now().strftime("%Y-%m-%d")
        deadline = pd.to_datetime(row['Filing_Deadline']).strftime('%d/%m/%Y')

        with col1:
            st.markdown(
                f'<span class="company-id-{row["Company_Number"]} company-name-text">{row["Company_Name"]}</span>'
                f'<span class="company-number-text">#{row["Company_Number"]}</span>',
                unsafe_allow_html=True
            )

        with col2:
            if is_overdue:
                st.markdown(f"<span class='overdue-text'>🔴 {deadline}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: #262730;'>{deadline}</span>", unsafe_allow_html=True)

        with col3:
            days_until = (pd.to_datetime(row['Filing_Deadline']) - datetime.now()).days
            if days_until < 0:
                st.markdown(f"<span style='font-size: 12px; color: #666;'>{abs(days_until)}d overdue</span>", unsafe_allow_html=True)
            elif days_until < 30:
                st.markdown(f"<span style='font-size: 12px; color: #666;'>⚠️ {days_until}d</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='font-size: 12px; color: #666;'>{days_until}d</span>", unsafe_allow_html=True)

        with col4:
            current_status = row['Internal_Status']
            current_index = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0

            new_status = st.selectbox(
                "Status",
                options=STATUS_OPTIONS,
                index=current_index,
                key=f"status_{row['Company_Number']}",
                label_visibility="collapsed"
            )

            if new_status != current_status:
                db.update_internal_status(row['Company_Number'], new_status)
                st.rerun()

# Bulk operations
st.markdown("---")
col_bulk1, col_bulk2, col_bulk3 = st.columns(3)

with col_bulk1:
    if st.button("📥 Export Excel", width='stretch'):
        try:
            export_df = df.copy()
            export_df['Filing_Deadline'] = pd.to_datetime(export_df['Filing_Deadline']).dt.strftime('%Y-%m-%d')
            export_df = export_df[['Company_Name', 'Company_Number', 'Filing_Deadline', 'Internal_Status']]

            excel_filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            export_df.to_excel(excel_filename, index=False)
            st.success(f"✅ {excel_filename}")
        except Exception as e:
            st.error(f"❌ {e}")

with col_bulk2:
    if st.button("📅 Refresh Deadlines", width='stretch'):
        try:
            api = CompaniesHouseAPI()
            refresh_df = db.search_companies(search_term) if search_term else db.get_all_companies()
            company_numbers = refresh_df['Company_Number'].tolist()

            with st.spinner(f"Fetching {len(company_numbers)}..."):
                results = api.bulk_get_filing_deadlines(company_numbers)
                updated_count = sum(1 for d in results.values() if d)

                for company_number, deadline in results.items():
                    if deadline:
                        db.update_filing_deadline(company_number, deadline)

                st.success(f"✅ Updated {updated_count}")
                st.rerun()

        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ {e}")

with col_bulk3:
    if st.button("📤 Re-Import", width='stretch'):
        try:
            import os
            use_api = bool(os.getenv("COMPANIES_HOUSE_API_KEY"))

            if use_api:
                with st.spinner("Importing..."):
                    count = db.import_from_excel("clients.xlsx", use_api_for_deadlines=True)
            else:
                count = db.import_from_excel("clients.xlsx", use_api_for_deadlines=False)

            if count > 0:
                st.success(f"✅ Imported {count}")
                st.rerun()
            else:
                st.info("ℹ️ No new companies")
        except Exception as e:
            st.error(f"❌ {e}")

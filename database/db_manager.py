"""
Database Manager for Company Accounts Dashboard.
Handles all SQLite database operations.
"""
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class DatabaseManager:
    """Manages all database operations for the company accounts system."""

    def __init__(self, db_path: str = "client_data.db"):
        """Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.initialize_database()

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection.

        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def initialize_database(self):
        """Create the database schema if it doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                Company_Number TEXT PRIMARY KEY,
                Company_Name TEXT NOT NULL,
                Filing_Deadline DATE NOT NULL,
                Internal_Status TEXT DEFAULT 'Not Started',
                Accounts_Filed_CH BOOLEAN DEFAULT 0,
                Last_Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def import_from_excel(self, excel_path: str, use_api_for_deadlines: bool = False) -> int:
        """Import company data from Excel file.

        Args:
            excel_path: Path to the Excel file
            use_api_for_deadlines: If True, fetch filing deadlines from Companies House API

        Returns:
            Number of companies imported
        """
        # Read Excel file
        df = pd.read_excel(excel_path)

        # Validate required columns (Filing_Deadline optional if using API)
        if use_api_for_deadlines:
            required_columns = ['Company_Name', 'Company_Number']
        else:
            required_columns = ['Company_Name', 'Company_Number', 'Filing_Deadline']

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Try to import Companies House API if using it for deadlines
        api = None
        if use_api_for_deadlines:
            try:
                from api import CompaniesHouseAPI
                import os
                if os.getenv("COMPANIES_HOUSE_API_KEY"):
                    api = CompaniesHouseAPI()
                    print("Using Companies House API for filing deadlines")
                else:
                    print("Warning: API key not set, falling back to Excel deadlines")
                    use_api_for_deadlines = False
            except Exception as e:
                print(f"Warning: Could not initialize API: {e}")
                use_api_for_deadlines = False

        conn = self.get_connection()
        cursor = conn.cursor()

        imported_count = 0
        for _, row in df.iterrows():
            try:
                # Get company details
                company_number = str(row['Company_Number'])
                company_name = str(row['Company_Name'])

                # Get filing deadline - try API first, fall back to Excel
                filing_deadline = None

                if use_api_for_deadlines and api:
                    try:
                        api_deadline = api.get_filing_deadline(company_number)
                        if api_deadline:
                            filing_deadline = api_deadline
                            print(f"  Fetched deadline from API for {company_number}: {api_deadline}")
                    except Exception as e:
                        print(f"  API error for {company_number}, using Excel deadline: {e}")

                # Fall back to Excel deadline if API didn't work
                if not filing_deadline and 'Filing_Deadline' in df.columns:
                    excel_deadline = row['Filing_Deadline']
                    if pd.notna(excel_deadline):
                        if isinstance(excel_deadline, pd.Timestamp):
                            filing_deadline = excel_deadline.strftime('%Y-%m-%d')
                        else:
                            filing_deadline = str(excel_deadline).split()[0]

                # Skip if no deadline found
                if not filing_deadline:
                    print(f"  Skipping {company_number}: No deadline available")
                    continue

                cursor.execute("""
                    INSERT OR IGNORE INTO companies
                    (Company_Number, Company_Name, Filing_Deadline, Internal_Status, Accounts_Filed_CH)
                    VALUES (?, ?, ?, 'Not Started', 0)
                """, (
                    company_number,
                    company_name,
                    filing_deadline
                ))
                if cursor.rowcount > 0:
                    imported_count += 1
            except Exception as e:
                print(f"Error importing {row['Company_Number']}: {e}")

        conn.commit()
        conn.close()

        return imported_count

    def get_all_companies(self) -> pd.DataFrame:
        """Get all companies as a pandas DataFrame.

        Returns:
            DataFrame containing all company data
        """
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM companies ORDER BY Filing_Deadline", conn)
        conn.close()
        return df

    def get_company(self, company_number: str) -> Optional[Dict]:
        """Get a single company by number.

        Args:
            company_number: The company number

        Returns:
            Dictionary containing company data or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE Company_Number = ?", (company_number,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def update_internal_status(self, company_number: str, new_status: str) -> bool:
        """Update the internal status of a company.

        Args:
            company_number: The company number
            new_status: The new status value

        Returns:
            True if successful, False otherwise
        """
        valid_statuses = [
            'Not Started',
            'Started',
            'Sent to Client',
            'Missing Information',
            'Ready to Submit'
        ]

        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE companies
            SET Internal_Status = ?, Last_Updated = CURRENT_TIMESTAMP
            WHERE Company_Number = ?
        """, (new_status, company_number))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def update_filing_status(self, company_number: str, filed: bool) -> bool:
        """Update the Companies House filing status.

        Args:
            company_number: The company number
            filed: Whether accounts have been filed

        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE companies
            SET Accounts_Filed_CH = ?, Last_Updated = CURRENT_TIMESTAMP
            WHERE Company_Number = ?
        """, (1 if filed else 0, company_number))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def update_filing_deadline(self, company_number: str, deadline: str) -> bool:
        """Update the filing deadline for a company.

        Args:
            company_number: The company number
            deadline: The filing deadline (YYYY-MM-DD format)

        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE companies
            SET Filing_Deadline = ?, Last_Updated = CURRENT_TIMESTAMP
            WHERE Company_Number = ?
        """, (deadline, company_number))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def get_kpi_counts(self, deadline_cutoff: str = "2026-07-31") -> Dict[str, int]:
        """Get KPI counts for the dashboard.

        Args:
            deadline_cutoff: The deadline cutoff date (YYYY-MM-DD)

        Returns:
            Dictionary with KPI counts
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Accounts Outstanding (Deadline <= cutoff and not filed)
        cursor.execute("""
            SELECT COUNT(*) FROM companies
            WHERE Filing_Deadline <= ? AND Accounts_Filed_CH = 0
        """, (deadline_cutoff,))
        outstanding = cursor.fetchone()[0]

        # Ready to Submit
        cursor.execute("""
            SELECT COUNT(*) FROM companies
            WHERE Internal_Status = 'Ready to Submit'
        """)
        ready = cursor.fetchone()[0]

        # Sent to Client
        cursor.execute("""
            SELECT COUNT(*) FROM companies
            WHERE Internal_Status = 'Sent to Client'
        """)
        sent = cursor.fetchone()[0]

        # Missing Information
        cursor.execute("""
            SELECT COUNT(*) FROM companies
            WHERE Internal_Status = 'Missing Information'
        """)
        missing = cursor.fetchone()[0]

        conn.close()

        return {
            'outstanding': outstanding,
            'ready': ready,
            'sent': sent,
            'missing': missing
        }

    def search_companies(self, search_term: str) -> pd.DataFrame:
        """Search companies by name or number.

        Args:
            search_term: The search term

        Returns:
            DataFrame containing matching companies
        """
        conn = self.get_connection()
        query = """
            SELECT * FROM companies
            WHERE Company_Name LIKE ? OR Company_Number LIKE ?
            ORDER BY Filing_Deadline
        """
        search_pattern = f"%{search_term}%"
        df = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern))
        conn.close()
        return df

    def get_database_stats(self) -> Dict[str, any]:
        """Get general database statistics.

        Returns:
            Dictionary containing database stats
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM companies")
        total_companies = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM companies WHERE Accounts_Filed_CH = 1")
        filed_count = cursor.fetchone()[0]

        conn.close()

        return {
            'total_companies': total_companies,
            'filed_count': filed_count,
            'unfiled_count': total_companies - filed_count
        }

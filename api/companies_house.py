"""
Companies House API integration.
Handles checking company filing statuses via the Companies House API.
"""
import os
import requests
from typing import Optional, Dict
from datetime import datetime


class CompaniesHouseAPI:
    """Interface for Companies House API operations."""

    BASE_URL = "https://api.company-information.service.gov.uk"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the API client.

        Args:
            api_key: Companies House API key. If not provided, reads from
                     COMPANIES_HOUSE_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("COMPANIES_HOUSE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Companies House API key is required. "
                "Set COMPANIES_HOUSE_API_KEY environment variable."
            )

        self.session = requests.Session()
        # Companies House uses HTTP Basic Auth with API key as username
        self.session.auth = (self.api_key, '')

    def get_company_profile(self, company_number: str) -> Optional[Dict]:
        """Get company profile information.

        Args:
            company_number: The company registration number

        Returns:
            Dictionary containing company profile data, or None if error

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        url = f"{self.BASE_URL}/company/{company_number}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Company {company_number} not found")
                return None
            else:
                raise
        except requests.exceptions.RequestException as e:
            print(f"Error fetching company {company_number}: {e}")
            return None

    def check_accounts_filed(self, company_number: str) -> Optional[bool]:
        """Check if accounts have been filed for a company.

        This checks the 'accounts' section of the company profile to determine
        if accounts have been filed recently.

        Args:
            company_number: The company registration number

        Returns:
            True if accounts have been filed, False if not, None if error

        Note:
            The Companies House API provides information about the last accounts
            filed. This method checks if accounts exist and have been filed.
        """
        profile = self.get_company_profile(company_number)

        if not profile:
            return None

        # Check if accounts section exists
        accounts = profile.get('accounts', {})

        # Check for last accounts information
        last_accounts = accounts.get('last_accounts', {})
        if last_accounts:
            # If last accounts exist, check the made_up_to date
            made_up_to = last_accounts.get('made_up_to')
            if made_up_to:
                # Accounts have been filed
                return True

        # Check for overdue status
        overdue = accounts.get('overdue', False)
        if overdue:
            return False

        # Default: if we have account information but no clear status
        return False

    def get_filing_deadline(self, company_number: str, verbose: bool = False) -> Optional[str]:
        """Get the next filing deadline for a company.

        Args:
            company_number: The company registration number
            verbose: If True, print detailed debugging information

        Returns:
            Filing deadline as ISO date string (YYYY-MM-DD), or None if error
        """
        profile = self.get_company_profile(company_number)

        if not profile:
            if verbose:
                print(f"  [{company_number}] No profile data returned from API")
            return None

        # Check company status
        company_status = profile.get('company_status', 'unknown')
        if verbose:
            print(f"  [{company_number}] Status: {company_status}")

        # Companies that don't need to file accounts
        exempt_statuses = ['dissolved', 'liquidation', 'receivership', 'administration']
        if company_status in exempt_statuses:
            if verbose:
                print(f"  [{company_number}] Company is {company_status} - no deadline required")
            return None

        # Get accounts information
        accounts = profile.get('accounts', {})

        if not accounts:
            if verbose:
                print(f"  [{company_number}] No accounts section in profile")
            return None

        # Try to get next_due date
        next_due = accounts.get('next_due')

        if next_due:
            if verbose:
                print(f"  [{company_number}] Found next_due: {next_due}")
            return next_due

        # If no next_due, provide more information
        if verbose:
            print(f"  [{company_number}] No next_due field. Available accounts fields: {list(accounts.keys())}")
            overdue = accounts.get('overdue', False)
            if overdue:
                print(f"  [{company_number}] Accounts are OVERDUE")

            last_accounts = accounts.get('last_accounts', {})
            if last_accounts:
                made_up_to = last_accounts.get('made_up_to')
                print(f"  [{company_number}] Last accounts made up to: {made_up_to}")

        return None

    def get_accounts_info(self, company_number: str) -> Optional[Dict]:
        """Get detailed accounts information for a company.

        Args:
            company_number: The company registration number

        Returns:
            Dictionary with accounts information including:
            - next_due: Next filing deadline
            - last_made_up_to: Last accounts period end date
            - overdue: Whether accounts are overdue
            - filed: Whether accounts have been filed
        """
        profile = self.get_company_profile(company_number)

        if not profile:
            return None

        accounts = profile.get('accounts', {})
        last_accounts = accounts.get('last_accounts', {})

        return {
            'next_due': accounts.get('next_due'),
            'last_made_up_to': last_accounts.get('made_up_to'),
            'overdue': accounts.get('overdue', False),
            'filed': bool(last_accounts),
            'accounting_reference_date': accounts.get('accounting_reference_date', {})
        }

    def bulk_check_filing_status(self, company_numbers: list) -> Dict[str, bool]:
        """Check filing status for multiple companies.

        Args:
            company_numbers: List of company numbers to check

        Returns:
            Dictionary mapping company numbers to filing status (True/False/None)
        """
        results = {}
        for company_number in company_numbers:
            try:
                filed = self.check_accounts_filed(company_number)
                results[company_number] = filed
            except Exception as e:
                print(f"Error checking {company_number}: {e}")
                results[company_number] = None

        return results

    def bulk_get_filing_deadlines(self, company_numbers: list, verbose: bool = False) -> Dict[str, Optional[str]]:
        """Get filing deadlines for multiple companies.

        Args:
            company_numbers: List of company numbers to check
            verbose: If True, print detailed debugging information

        Returns:
            Dictionary mapping company numbers to filing deadlines (YYYY-MM-DD format)
        """
        results = {}
        total = len(company_numbers)

        for idx, company_number in enumerate(company_numbers, 1):
            try:
                if verbose:
                    print(f"[{idx}/{total}] Checking {company_number}...")

                deadline = self.get_filing_deadline(company_number, verbose=verbose)
                results[company_number] = deadline

                if not verbose and not deadline:
                    # Still print skips in non-verbose mode
                    print(f"  Skipping {company_number}: No deadline available")

            except Exception as e:
                print(f"  Error fetching deadline for {company_number}: {e}")
                results[company_number] = None

        return results

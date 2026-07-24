"""
Daily Loader - Orchestrates file discovery, parsing, FX rates, and database storage
"""

from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from loaders.file_discovery import DailyFileDiscovery, FileDiscoveryError
from loaders.csv_parsers import ParserFactory, ParseError
from database.connection import DatabaseConnection
from fx_rates_fetcher import FXRateFetcher


class DailyLoadError(Exception):
    """Raised when daily load fails."""
    pass


class DailyLoader:
    """
    Orchestrates the complete daily margin data load process.

    Steps:
    1. Discover all 7 CSV files on network drives
    2. Fetch FX rates for the date
    3. Parse each CSV file
    4. Convert multi-currency values to GBP
    5. Store in database
    6. Record audit trail
    """

    def __init__(self, db_path: str = 'data/margin_recon.db'):
        """
        Initialize daily loader.

        Args:
            db_path: Path to SQLite database
        """
        self.db = DatabaseConnection(db_path)
        self.fx_fetcher = FXRateFetcher()

    def load_date(self, business_date: date, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load all margin data for a specific business date.

        Args:
            business_date: Date to load data for
            force_reload: If True, reload even if data exists

        Returns:
            Summary dict with load statistics

        Raises:
            DailyLoadError: If load fails
        """
        load_start = datetime.now()

        try:
            # Step 1: Check if already loaded
            if not force_reload and self._is_date_loaded(business_date):
                return {
                    'status': 'SKIPPED',
                    'reason': 'Data already loaded',
                    'business_date': business_date,
                }

            # Step 2: Discover files
            print(f"\n[{business_date}] Discovering files...")
            discovery = DailyFileDiscovery(business_date)
            files = discovery.discover_all_files()
            print(discovery.get_file_summary(files))

            # Step 3: Fetch FX rates
            print(f"\n[{business_date}] Fetching FX rates...")
            fx_rates = self._fetch_fx_rates(business_date)
            print(f"  EUR: {fx_rates['EUR']:.4f}, USD: {fx_rates['USD']:.4f}, GBP: {fx_rates['GBP']:.4f}")

            # Step 4: Parse files and store data
            print(f"\n[{business_date}] Parsing files...")
            total_records = 0
            parse_results = {}

            for file_type, source_file in files.items():
                if not source_file.exists:
                    print(f"  SKIP: {file_type} (file not found)")
                    parse_results[file_type] = {'status': 'MISSING', 'records': 0}
                    continue

                try:
                    records = self._parse_and_store(
                        file_type,
                        source_file.file_path,
                        business_date,
                        fx_rates
                    )
                    total_records += records
                    parse_results[file_type] = {'status': 'SUCCESS', 'records': records}
                    print(f"  OK: {file_type} ({records} records)")

                except ParseError as e:
                    print(f"  ERROR: {file_type} - {e}")
                    parse_results[file_type] = {'status': 'ERROR', 'records': 0, 'error': str(e)}

            # Step 5: Record audit trail
            load_duration = (datetime.now() - load_start).total_seconds()
            self._record_load(business_date, parse_results, load_duration)

            print(f"\n[{business_date}] Load complete: {total_records} records in {load_duration:.1f}s")

            return {
                'status': 'SUCCESS',
                'business_date': business_date,
                'total_records': total_records,
                'duration_seconds': load_duration,
                'files': parse_results,
            }

        except FileDiscoveryError as e:
            raise DailyLoadError(f"File discovery failed: {e}")
        except Exception as e:
            raise DailyLoadError(f"Load failed: {e}")

    def _is_date_loaded(self, business_date: date) -> bool:
        """Check if data for this date already exists in database."""
        cursor = self.db.conn.execute(
            "SELECT COUNT(*) FROM margin_positions WHERE business_date = ?",
            (business_date.isoformat(),)
        )
        count = cursor.fetchone()[0]
        return count > 0

    def _fetch_fx_rates(self, business_date: date) -> Dict[str, float]:
        """
        Fetch FX rates for the business date.

        Args:
            business_date: Date to fetch rates for

        Returns:
            Dict with EUR, USD, GBP rates to GBP
        """
        rates = self.fx_fetcher.fetch_rates_to_gbp(business_date)

        # Store in database
        for currency, rate in rates.items():
            if currency != 'GBP':  # GBP to GBP is always 1.0
                self.db.store_fx_rate(
                    business_date=business_date,
                    currency_from=currency,
                    currency_to='GBP',
                    rate=rate,
                    source=self.fx_fetcher.primary_source
                )

        return rates

    def _parse_and_store(
        self,
        file_type: str,
        file_path: Path,
        business_date: date,
        fx_rates: Dict[str, float]
    ) -> int:
        """
        Parse a CSV file and store results in database.

        Args:
            file_type: Type of file (e.g., 'bnp_cel_mc')
            file_path: Path to CSV file
            business_date: Business date for this data
            fx_rates: FX rates dict for currency conversion

        Returns:
            Number of records stored
        """
        # Get appropriate parser
        parser = ParserFactory.get_parser(file_type)

        # Parse file
        if file_type in ['bnp_cel_mc', 'bnp_cet_mc']:
            entity = 'CEL' if 'cel' in file_type else 'CET'
            parsed_data = parser.parse(file_path, business_date, entity)
        else:
            parsed_data = parser.parse(file_path, business_date)

        # Ensure parsed_data is a list
        if not isinstance(parsed_data, list):
            parsed_data = [parsed_data]

        # Store in database
        records_stored = 0
        for record in parsed_data:
            # Convert to GBP if needed
            original_currency = record.get('original_currency', 'GBP')
            native_value = record.get('position_value_native', 0)

            if original_currency in fx_rates:
                gbp_value = native_value * fx_rates[original_currency]
            else:
                gbp_value = native_value  # Assume already in GBP

            # Store position
            self.db.store_margin_position(
                business_date=business_date,
                clearer=record.get('clearer', 'UNKNOWN'),
                margin_type=record.get('margin_type', 'UNKNOWN'),
                entity=record.get('entity', 'UNKNOWN'),
                counterparty=record.get('counterparty', 'UNKNOWN'),
                original_currency=original_currency,
                position_value_native=native_value,
                position_value_gbp=gbp_value,
                product=record.get('product_name', None),
                commodity=record.get('commodity', None),
                source_file=str(file_path)
            )

            records_stored += 1

        return records_stored

    def _record_load(
        self,
        business_date: date,
        parse_results: Dict[str, Dict[str, Any]],
        duration_seconds: float
    ):
        """
        Record load audit trail in database.

        Args:
            business_date: Date that was loaded
            parse_results: Results from each file parse
            duration_seconds: Total load duration
        """
        # TODO: Create data_loads audit table
        # For now, just print summary
        pass


def main():
    """Demo: Load data for a specific date."""
    import argparse

    parser = argparse.ArgumentParser(description='Load daily margin data')
    parser.add_argument('date', help='Business date (YYYY-MM-DD)')
    parser.add_argument('--force', action='store_true', help='Force reload even if data exists')
    parser.add_argument('--db', default='data/margin_recon.db', help='Database path')

    args = parser.parse_args()

    # Parse date
    business_date = date.fromisoformat(args.date)

    # Run loader
    loader = DailyLoader(db_path=args.db)

    try:
        result = loader.load_date(business_date, force_reload=args.force)
        print(f"\nResult: {result['status']}")
        if result['status'] == 'SUCCESS':
            print(f"Loaded {result['total_records']} records in {result['duration_seconds']:.1f}s")
    except DailyLoadError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

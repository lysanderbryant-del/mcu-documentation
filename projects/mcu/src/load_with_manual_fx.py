"""
Load daily data with manually-entered FX rates (for testing when APIs blocked)
"""

from datetime import date, datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from loaders.file_discovery import DailyFileDiscovery
from loaders.csv_parsers import ParserFactory
from database.connection import DatabaseConnection

def load_date_with_manual_fx(business_date: date, db_path: str = 'data/margin_recon.db'):
    """Load data using pre-populated FX rates."""

    load_start = datetime.now()
    db = DatabaseConnection(db_path)

    print(f"\n[{business_date}] Discovering files...")
    discovery = DailyFileDiscovery(business_date)
    files = discovery.discover_all_files()
    print(discovery.get_file_summary(files))

    print(f"\n[{business_date}] Loading FX rates from database...")
    cursor = db.conn.execute(
        "SELECT currency_from, rate FROM fx_rates WHERE business_date=? AND currency_to='GBP'",
        (business_date.isoformat(),)
    )
    fx_rates = {row[0]: row[1] for row in cursor.fetchall()}

    if not fx_rates:
        print("ERROR: No FX rates found in database. Please insert manually first.")
        return

    print(f"  Rates: {fx_rates}")

    print(f"\n[{business_date}] Parsing files...")
    total_records = 0

    for file_type, source_file in files.items():
        if not source_file.exists:
            print(f"  SKIP: {file_type} (file not found)")
            continue

        try:
            parser = ParserFactory.get_parser(file_type)

            # Parse based on type
            if file_type in ['bnp_cel_mc', 'bnp_cet_mc']:
                entity = 'CEL' if 'cel' in file_type else 'CET'
                parsed_data = parser.parse(source_file.file_path, business_date, entity)
            else:
                parsed_data = parser.parse(source_file.file_path, business_date)

            # Ensure list
            if not isinstance(parsed_data, list):
                parsed_data = [parsed_data]

            # Store records
            for record in parsed_data:
                original_currency = record.get('original_currency', 'GBP')
                native_value = record.get('position_value_native', 0)

                # Convert to GBP
                if original_currency in fx_rates:
                    gbp_value = native_value * fx_rates[original_currency]
                else:
                    gbp_value = native_value

                db.store_margin_position(
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
                    source_file=str(source_file.file_path)
                )

                total_records += 1

            print(f"  OK: {file_type} ({len(parsed_data)} records)")

        except Exception as e:
            print(f"  ERROR: {file_type} - {e}")
            import traceback
            traceback.print_exc()

    load_duration = (datetime.now() - load_start).total_seconds()
    print(f"\n[{business_date}] Load complete: {total_records} records in {load_duration:.1f}s")

    db.conn.close()
    return total_records


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Load daily margin data (manual FX)')
    parser.add_argument('date', help='Business date (YYYY-MM-DD)')
    parser.add_argument('--db', default='data/margin_recon.db', help='Database path')

    args = parser.parse_args()
    business_date = date.fromisoformat(args.date)

    load_date_with_manual_fx(business_date, db_path=args.db)

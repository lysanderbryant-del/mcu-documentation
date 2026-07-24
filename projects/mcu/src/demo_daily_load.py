"""
Demo: Daily Loader Workflow

This script demonstrates the complete daily load process:
1. File discovery
2. FX rate fetching
3. CSV parsing
4. Database storage
"""

from datetime import date
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from loaders.file_discovery import DailyFileDiscovery


def demo_file_discovery():
    """Demonstrate file discovery for multiple dates."""
    print("=" * 70)
    print("DEMO: FILE DISCOVERY")
    print("=" * 70)

    test_dates = [
        date(2026, 7, 22),  # Actual data date from Excel
        date(2026, 7, 23),  # Today
        date(2026, 6, 30),  # Previous month
    ]

    for test_date in test_dates:
        print(f"\n{test_date.strftime('%A, %B %d, %Y')}")
        print("-" * 70)

        discovery = DailyFileDiscovery(test_date)

        # Show date formats
        print(f"\nDate Formats:")
        print(f"  ISO:        {discovery.date_iso}")
        print(f"  Compact:    {discovery.date_compact}")
        print(f"  Underscore: {discovery.date_underscore}")
        print(f"  Month:      {discovery.month_folder}")

        # Show expected file paths
        print(f"\nExpected Files:")

        files = {
            'BNP CEL MC': discovery._find_bnp_mc_statement('CEL'),
            'BNP CEL OTE': discovery._find_bnp_ote_detail('CEL'),
            'BNP CEL Journals': discovery._find_bnp_journal_entries('CEL'),
            'BNP CEL PnS': discovery._find_bnp_pns('CEL'),
            'BNP CET MC': discovery._find_bnp_mc_statement('CET'),
            'SocGen': discovery._find_socgen_margin(),
            'CSA': discovery._find_csa_collateral(),
        }

        for name, source_file in files.items():
            status = "EXISTS" if source_file.exists else "NOT FOUND"
            print(f"  [{status:10s}] {name}")
            if source_file.exists:
                size_mb = source_file.size_bytes / (1024 * 1024)
                print(f"               Size: {size_mb:.2f} MB")
                print(f"               Path: {source_file.file_path}")
            else:
                print(f"               Expected: {source_file.file_path.name}")


def demo_load_workflow():
    """Demonstrate complete daily load workflow."""
    print("\n\n" + "=" * 70)
    print("DEMO: DAILY LOAD WORKFLOW")
    print("=" * 70)

    print("""
The daily load process follows these steps:

STEP 1: FILE DISCOVERY
  - Scan network drives for all 7 CSV files
  - Check file existence and timestamps
  - Validate file sizes

STEP 2: FX RATE FETCHING
  - Call Frankfurter API (ECB data)
  - Get EUR, USD, GBP rates
  - Store rates in database

STEP 3: PARSE CSV FILES
  - BNP CEL MC Statement     -> Multi-currency margin totals
  - BNP CEL OTE Detail       -> Product-level breakdown
  - BNP CEL Journal Entries  -> Spot/physical delivery
  - BNP CEL PnS              -> Cascade P&L
  - BNP CET MC Statement     -> CET entity margin
  - SocGen Global Margin     -> SocGen margin value
  - CSA Collateral Summary   -> OTC collateral

STEP 4: CURRENCY CONVERSION
  - Convert all positions to GBP
  - Apply FX rates from Step 2
  - Store both native and GBP values

STEP 5: DATABASE STORAGE
  - Insert into margin_positions table
  - Insert into ote_detail table
  - Record audit trail

STEP 6: VALIDATION
  - Verify total margin matches expected
  - Check for missing files
  - Alert on anomalies

Example Usage:
  python src/loaders/daily_loader.py 2026-07-22
  python src/loaders/daily_loader.py 2026-07-23 --force
    """)


def demo_scheduled_execution():
    """Show how daily load would be scheduled."""
    print("\n\n" + "=" * 70)
    print("DEMO: SCHEDULED EXECUTION")
    print("=" * 70)

    print("""
The daily load can be scheduled using Windows Task Scheduler:

SCHEDULE: Daily at 5:30 PM (after market close)

Task Configuration:
  Name:     Daily Margin Load
  Trigger:  Daily at 17:30
  Action:   Run Python script
  Command:  python "C:\\...\\daily_loader.py" "$(Get-Date -Format 'yyyy-MM-dd')"

Alternative: Use a batch file that:
  1. Determines today's date
  2. Runs daily_loader.py with --force if needed
  3. Logs output to file
  4. Sends email notification on completion/failure

Example batch script (load_today.bat):

  @echo off
  set TODAY=%date:~10,4%-%date:~4,2%-%date:~7,2%
  python src\\loaders\\daily_loader.py %TODAY% > logs\\load_%TODAY%.log 2>&1
  if errorlevel 1 (
      echo Load failed! >> logs\\errors.log
  ) else (
      echo Load succeeded for %TODAY% >> logs\\success.log
  )

Network Drive Authentication:
  - Ensure service account has read access to all 4 network locations
  - Store credentials in Windows Credential Manager
  - Test file access before scheduling
    """)


if __name__ == "__main__":
    demo_file_discovery()
    demo_load_workflow()
    demo_scheduled_execution()

    print("\n" + "=" * 70)
    print("To test the actual loader (requires network access):")
    print("  python src/loaders/daily_loader.py 2026-07-22")
    print("=" * 70 + "\n")

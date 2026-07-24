"""
File Discovery Demo - Show how files are located for any business date
"""

from pathlib import Path
from datetime import date, datetime, timedelta

def format_date_examples(business_date: date):
    """Show all date format variations needed for file discovery."""

    print(f"\n{'='*60}")
    print(f"FILE DISCOVERY FOR: {business_date.strftime('%A, %B %d, %Y')}")
    print(f"{'='*60}\n")

    # Date formatting variations
    date_iso = business_date.strftime('%Y-%m-%d')        # 2026-07-22
    date_compact = business_date.strftime('%Y%m%d')      # 20260722
    date_underscore = business_date.strftime('%Y_%m_%d') # 2026_07_22
    month_folder = business_date.strftime('%Y-%b')       # 2026-Jul
    date_ddmmyyyy = business_date.strftime('%d%m%Y')     # 23072026

    print(f"Date Formats Required:")
    print(f"  ISO format:         {date_iso}")
    print(f"  Compact:            {date_compact}")
    print(f"  Underscore:         {date_underscore}")
    print(f"  Month folder:       {month_folder}")
    print(f"  DD/MM/YYYY:         {date_ddmmyyyy}")
    print()

    # Base paths
    bnp_base = "\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\BNPFileStore"
    bnp_processed = f"{bnp_base}\\Processed\\{month_folder}"

    bnpcet_base = "\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\BNPCETFileStore"
    bnpcet_processed = f"{bnpcet_base}\\Processed\\{month_folder}"

    socgen_base = "\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\SGSAFileStore\\SocGenAAL"

    csa_base = "\\\\app-nas-fsx-prod.uk.centricaplc.com\\CRR_PROD_01\\CreditRisk\\Collateral"

    print("EXPECTED FILE PATHS:")
    print(f"\n1. BNP CEL - Margin Call Statement")
    print(f"   {bnp_processed}\\")
    print(f"   MC_Statement_CEL U_{date_iso}_{date_ddmmyyyy}_HH_MM_SS.csv")

    print(f"\n2. BNP CEL - Open Trade Equity Detail")
    print(f"   {bnp_processed}\\")
    print(f"   Detailed_Open_Pos_CEL U_{date_iso}_{date_ddmmyyyy}_HH_MM_SS.csv")

    print(f"\n3. BNP CEL - Journal Entries")
    print(f"   {bnp_processed}\\")
    print(f"   Journal_Entries_CEL U_{date_iso}_{date_ddmmyyyy}_HH_MM_SS.csv")

    print(f"\n4. BNP CEL - P&L Cascade")
    print(f"   {bnp_processed}\\")
    print(f"   PnS_CEL U_{date_iso}_{date_ddmmyyyy}_HH_MM_SS.csv")

    print(f"\n5. BNP CET - Margin Call Statement")
    print(f"   {bnpcet_processed}\\")
    print(f"   MC_Statement_CET U_{date_iso}_{date_ddmmyyyy}_HH_MM_SS.csv")

    print(f"\n6. SocGen - Global Margin Report")
    print(f"   {socgen_base}\\")
    print(f"   {date_compact}_GlobalMarginUnderlyingCurrencyReport.csv")

    print(f"\n7. CSA - Collateral Summary")
    print(f"   {csa_base}\\")
    print(f"   Collateral_Summary_{date_underscore}_HHMMSS.csv")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Show examples for multiple dates

    # Example 1: July 22, 2026 (actual data date from Excel)
    format_date_examples(date(2026, 7, 22))

    # Example 2: July 23, 2026 (today)
    format_date_examples(date(2026, 7, 23))

    # Example 3: A date from previous month
    format_date_examples(date(2026, 6, 30))

    # Example 4: End of year (different month folder format)
    format_date_examples(date(2025, 12, 31))

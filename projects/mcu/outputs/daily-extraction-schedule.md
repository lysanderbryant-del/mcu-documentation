# Daily Extraction Schedule: Complete Source File List

**Date**: 2026-07-23  
**Purpose**: Define all CSV files required for automated daily margin report generation

---

## Executive Summary

**7 CSV files required daily** to generate the complete £65.11M margin report:

| # | Component | Amount | Filename | Network Location | Status |
|---|-----------|---------|----------|------------------|--------|
| 1 | BNP CEL Summary | £52.66M | MC_Statement_CEL U_*.csv | BNPFileStore/Processed | ✅ |
| 2 | BNP CEL OTE Detail | £29.46M | Detailed_Open_Pos_CEL U_*.csv | BNPFileStore/Processed | ✅ |
| 3 | BNP CEL Spot/Physical | £23.51M | Journal_Entries_CEL U_*.csv | BNPFileStore/Processed | ✅ |
| 4 | BNP CEL Cascade P&L | -£0.28M | PnS_CEL U_*.csv | BNPFileStore/Processed | ✅ |
| 5 | BNP CET Summary | £0.73M | MC_Statement_CET U_*.csv | BNPCETFileStore/Processed | ✅ |
| 6 | SocGen Summary | £0.00M | *_GlobalMarginReport.csv | SGSAFileStore/SocGenAAL | ✅ |
| 7 | CSA Collateral | £11.72M | Collateral_Summary_*.csv | CreditRisk/Collateral | ✅ |

---

## Detailed File Specifications

### 1. BNP CEL - Margin Call Statement (£52.66M Total)

**Purpose**: Overall margin position aggregated by currency

**Filename**: `MC_Statement_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Example**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\MC_Statement_CEL U_2026-07-22_23072026_07_22_38.csv
```

**Excel Tab**: `CEL_BNP_SUM`

**Key Columns to Extract**:
- BA: NLV (Net Liquidation Value)
- AB: ORIGINAL_CURRENCY (EUR/GBP/USD)
- AA: BASE_CURRENCY (EUR)
- Z: CURRENCY_1 (filter = 0)

**Extraction Logic**:
```sql
SELECT 
    business_date,
    original_currency,
    SUM(nlv) as margin_value
FROM mc_statement_cel
WHERE base_currency = 'EUR'
  AND currency_flag = 0
GROUP BY original_currency
```

**Output**: Multi-currency totals (EUR, GBP, USD)

---

### 2. BNP CEL - Open Trade Equity Detail (£29.46M)

**Purpose**: Product-level breakdown of open positions

**Filename**: `Detailed_Open_Pos_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Paths** (TWO locations):
```
Pre-BNPP:  \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\endur_in\
Post-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Recommendation**: Use **Post-BNPP (Processed)** folder for consistency

**Example**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\Detailed_Open_Pos_CEL U_2026-07-22_23072026_07_22_37.csv
```

**Excel Tab**: `CELOteData` → Pivot: `BnppCelOtePivot`

**Key Columns to Extract**:
- PRODUCT / EXCHANGE_PRODUCT_DESCRIPTION
- OTE (Open Trade Equity value)
- CURRENCY
- CONTRACT_TYPE (Future/Option)
- Plus dates for movement calculation

**Extraction Logic**:
```sql
SELECT 
    business_date,
    product_name,
    commodity,
    contract_type,
    currency,
    SUM(ote_value) as ote_total
FROM detailed_open_positions
WHERE business_date = :date
GROUP BY product_name, commodity, currency
```

**Output**: Product-level OTE positions

---

### 3. BNP CEL - Spot/Physical Delivery (£23.51M)

**Purpose**: Daily settlement and physical delivery cashflows

**Filename**: `Journal_Entries_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Paths** (TWO locations):
```
Pre-BNPP:  \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\endur_in\
Post-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Recommendation**: Use **Post-BNPP (Processed)** folder

**Example**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\Journal_Entries_CEL U_2026-07-22_23072026_07_22_38.csv
```

**Excel Tab**: `CEL_JNLS` → Pivot: `Journal_Entries_CEL_U_Pivot`

**Key Columns to Extract** (from header row 10):
- COB Date (Column D)
- Exchange (Column E)
- Journal Type (Column F)
- Party (Column I)
- Amount (Column K)
- Description (Column M, N)

**Extraction Logic**:
```sql
SELECT 
    business_date,
    SUM(settlement_amount) as spot_physical_total
FROM journal_entries
WHERE business_date = :date
  AND clearer = 'BNP'
  AND entity = 'CEL'
  AND journal_type IN ('Cash Movement / Transfer', 'Physical Delivery')
```

**Output**: Spot/Physical delivery total

---

### 4. BNP CEL - P&L on Expiry/Cascading (-£0.28M)

**Purpose**: P&L from expired contracts that cascade/roll

**Filename**: `PnS_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Paths** (TWO locations):
```
Pre-BNPP:  \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\endur_in\
Post-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Recommendation**: Use **Post-BNPP (Processed)** folder

**Example**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\PnS_CEL U_2026-07-22_23072026_HH_MM_SS.csv
```

**Excel Tab**: `CELBNPCASCADEPNL` → Pivot: `PNLPIVOT`

**Key Columns to Extract** (from header row 10):
- COB Date (Column C)
- Clearer (Column H)
- Party (Column J)
- Product Type (Column M)
- Product (Column N)
- P&L Amount (needs identification)

**Extraction Logic**:
```sql
SELECT 
    business_date,
    SUM(pnl_amount) as cascade_pnl_total
FROM pns_cascade
WHERE business_date = :date
  AND clearer = 'BNP'
  AND entity = 'CEL'
  AND pnl_type = 'Expiry/Cascading'
```

**Output**: Cascade P&L total

---

### 5. BNP CET - Margin Call Statement (£0.73M)

**Purpose**: CET entity margin (Nordics trading)

**Filename**: `MC_Statement_CET U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore\Processed\YYYY-MMM\
```

**Example**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore\Processed\2026-Jul\MC_Statement_CET U_2026-07-22_23072026_07_00_43.csv
```

**Excel Tab**: `CETBNPSUM`

**Key Columns**: Same structure as CEL_BNP_SUM (BA, AB, AA, Z)

**Extraction Logic**: Same as File #1, but for CET entity

**Output**: CET margin by currency

---

### 6. SocGen - Global Margin Report (£0.00M)

**Purpose**: Société Générale margin call

**Filename**: `YYYYMMDD_GlobalMarginUnderlyingCurrencyReport.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\
```

**Example**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\20260722_GlobalMarginUnderlyingCurrencyReport.csv
```

**Excel Tab**: `SocGenMarginCall`

**Alternative Source**: Daily email from pulse-scheduler@sgcib.com with subject "EXT Global Margin report 1-008-E1800"

**Key Data**: Single margin value (typically in cell A7 of SocGenMarginCall tab)

**Extraction Logic**:
```sql
SELECT 
    business_date,
    margin_value
FROM socgen_margin
WHERE business_date = :date
```

**Output**: Single SocGen margin value

**Note**: File format may be different from BNP files. Needs investigation of actual CSV structure.

---

### 7. CSA - Collateral Summary (£11.72M)

**Purpose**: OTC collateral posted/held with counterparties

**Filename**: `Collateral_Summary_YYYY_MM_DD_HHMMSS.csv`

**Network Path**:
```
\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\
```

**Example**:
```
\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\Collateral_Summary_2026_07_23_074004.csv
```

**Excel Tabs**: `CsaCollateral` → Split into `CsaCel` and `CsaCet`

**Key Columns to Extract** (from header row 7):
- EOD (Date)
- Our_Entity (CEL or CET)
- Trading_Counterparty
- Collateral_Type (Cash, Standby LC)
- HeldGbpM (collateral we hold)
- PledgedGbpM (collateral we pledged)
- FxRate
- Currency (implied from calculation)

**Extraction Logic**:
```sql
SELECT 
    business_date,
    our_entity,
    currency,
    SUM(held_gbp_m - pledged_gbp_m) as net_collateral
FROM csa_collateral
WHERE business_date = :date
  AND our_entity IN ('Centrica Energy Limited', 'Centrica Energy Trading')
GROUP BY our_entity, currency
```

**Output**: CSA collateral by entity and currency

---

## Daily Extraction Workflow

### Schedule: 5:30 PM Daily (After Market Close)

```
STEP 1: DISCOVER FILES (5:30 PM)
├─ Scan BNP folders for today's files
├─ Scan SocGen folder for today's file
└─ Scan CSA folder for today's file

STEP 2: VALIDATE FILES (5:32 PM)
├─ Check all 7 files exist
├─ Check file sizes > 0
├─ Check timestamps are today
└─ Alert if any missing

STEP 3: FETCH FX RATES (5:35 PM)
└─ Call Frankfurter API for EUR, USD, GBP rates

STEP 4: PARSE FILES (5:36 PM)
├─ File 1: MC_Statement_CEL → Extract NLV by currency
├─ File 2: Detailed_Open_Pos_CEL → Extract OTE by product
├─ File 3: Journal_Entries_CEL → Extract spot/physical
├─ File 4: PnS_CEL → Extract cascade P&L
├─ File 5: MC_Statement_CET → Extract CET margin
├─ File 6: SocGen GlobalMargin → Extract margin value
└─ File 7: Collateral_Summary → Extract CSA by currency

STEP 5: STORE IN DATABASE (5:40 PM)
├─ Insert into margin_positions table
├─ Insert into ote_detail table
├─ Insert into fx_rates table
└─ Insert into data_loads table (audit trail)

STEP 6: CALCULATE SUMMARY (5:42 PM)
├─ Aggregate by counterparty
├─ Calculate "Other" breakdown if > £5M
└─ Store in daily_summary table

STEP 7: GENERATE REPORT (5:43 PM)
├─ Create daily margin report
├─ Compare to previous day
├─ Flag significant movements
└─ Export to Excel/PDF

STEP 8: NOTIFICATIONS (5:45 PM)
├─ Email report to distribution list
└─ Alert if any anomalies detected
```

---

## File Discovery Algorithm

```python
from pathlib import Path
from datetime import date

def discover_daily_files(business_date: date) -> dict:
    """
    Locate all 7 required CSV files for a business date.
    Returns dict with file paths or raises error if any missing.
    """
    
    # Date formatting
    date_iso = business_date.strftime('%Y-%m-%d')        # 2026-07-22
    date_compact = business_date.strftime('%Y%m%d')      # 20260722
    date_underscore = business_date.strftime('%Y_%m_%d') # 2026_07_22
    month_folder = business_date.strftime('%Y-%b')       # 2026-Jul
    
    # Base paths
    bnp_base = Path('\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\BNPFileStore')
    bnp_processed = bnp_base / 'Processed' / month_folder
    
    bnpcet_base = Path('\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\BNPCETFileStore')
    bnpcet_processed = bnpcet_base / 'Processed' / month_folder
    
    socgen_base = Path('\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\SGSAFileStore\\SocGenAAL')
    
    csa_base = Path('\\\\app-nas-fsx-prod.uk.centricaplc.com\\CRR_PROD_01\\CreditRisk\\Collateral')
    
    # Find files (using glob patterns)
    files = {
        'bnp_cel_mc': find_latest(bnp_processed, f'MC_Statement_CEL U_{date_iso}_*.csv'),
        'bnp_cel_ote': find_latest(bnp_processed, f'Detailed_Open_Pos_CEL U_{date_iso}_*.csv'),
        'bnp_cel_jnls': find_latest(bnp_processed, f'Journal_Entries_CEL U_{date_iso}_*.csv'),
        'bnp_cel_pns': find_latest(bnp_processed, f'PnS_CEL U_{date_iso}_*.csv'),
        'bnp_cet_mc': find_latest(bnpcet_processed, f'MC_Statement_CET U_{date_iso}_*.csv'),
        'socgen': find_latest(socgen_base, f'{date_compact}_GlobalMarginUnderlyingCurrencyReport.csv'),
        'csa': find_latest(csa_base, f'Collateral_Summary_{date_underscore}_*.csv'),
    }
    
    # Validate all found
    missing = [k for k, v in files.items() if v is None]
    if missing:
        raise FileNotFoundError(f"Missing files for {business_date}: {missing}")
    
    return files

def find_latest(directory: Path, pattern: str) -> Path:
    """Find the most recent file matching pattern."""
    matches = list(directory.glob(pattern))
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)
```

---

## Error Handling

### Missing Files

| File Missing | Impact | Action |
|--------------|--------|--------|
| BNP CEL MC | Cannot calculate total | **CRITICAL** - Alert immediately |
| BNP CEL OTE | No product breakdown | **HIGH** - Use previous day's breakdown |
| BNP CEL Journals | No spot/physical | **MEDIUM** - Flag in report |
| BNP CEL PnS | No cascade P&L | **LOW** - Usually small amount |
| BNP CET MC | No CET component | **MEDIUM** - Flag in report |
| SocGen | No SocGen component | **LOW** - Often zero |
| CSA | No CSA component | **HIGH** - Significant value |

### File Validation Checks

```python
def validate_file(file_path: Path, business_date: date) -> dict:
    """
    Validate file before parsing.
    Returns dict with validation results.
    """
    checks = {
        'exists': file_path.exists(),
        'not_empty': file_path.stat().st_size > 0 if file_path.exists() else False,
        'is_today': False,
        'readable': False,
    }
    
    if checks['exists']:
        # Check file timestamp
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).date()
        checks['is_today'] = mod_time == business_date
        
        # Check readable
        try:
            with open(file_path, 'r') as f:
                f.read(100)
            checks['readable'] = True
        except Exception:
            checks['readable'] = False
    
    checks['valid'] = all(checks.values())
    return checks
```

---

## Audit Trail

Every daily load must record:

```sql
INSERT INTO data_loads (
    business_date,
    source_file_path,
    source_file_type,
    parser_version,
    status,
    records_loaded,
    error_message,
    load_duration_seconds
) VALUES (
    '2026-07-22',
    '\\pgb1...\MC_Statement_CEL U_2026-07-22_*.csv',
    'BNP_MC_STATEMENT',
    '1.0',
    'SUCCESS',
    3,  -- 3 currency rows loaded
    NULL,
    2.5
)
```

---

## Summary: Complete Daily Extraction

**7 CSV Files** from **4 Network Locations**:

1. **BNPFileStore/Processed/** (4 files - BNP CEL)
   - MC_Statement
   - Detailed_Open_Pos
   - Journal_Entries
   - PnS

2. **BNPCETFileStore/Processed/** (1 file - BNP CET)
   - MC_Statement

3. **SGSAFileStore/SocGenAAL/** (1 file - SocGen)
   - GlobalMarginReport

4. **CreditRisk/Collateral/** (1 file - CSA)
   - Collateral_Summary

**Total Daily Report**: £65.11M with complete drill-down capability

---

*Daily extraction schedule complete. Ready for automated implementation.*

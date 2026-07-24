# Complete Source File Mapping for Daily Margin Report

**Date**: 2026-07-23  
**Purpose**: Map all CSV source files needed to generate the complete daily margin report with drill-down analysis

---

## Daily Report Summary: £65.11M

| Counterparty | Amount | Source Files Required |
|--------------|--------|----------------------|
| BNP CEL | £52.66M | 4 CSV files |
| BNP CET | £0.73M | 1 CSV file |
| SocGen | £0.00M | 1 CSV file |
| CSA | £11.72M | 1 CSV file |
| **TOTAL** | **£65.11M** | **7 CSV files total** |

---

## BNP CEL Breakdown (£52.66M) - 4 Source Files

### Component Analysis

```
Total OTE (Open Trade Equity):      £29.46M
  ├─ TTF Gas products              £46.97M
  ├─ NBP Gas                       £12.16M
  ├─ JKM (short)                  -£24.75M
  ├─ TFU TTF (short)              -£12.57M
  └─ Other                          £7.65M

Spot/Physical Delivery:             £23.51M
PNL on Expiry/Cascading:           -£0.28M
Other (Unexplained):               -£0.03M
─────────────────────────────────────────
BNP CEL Total:                     £52.66M ✓
```

### Source File 1: MC_Statement (Margin Call Summary)

**Purpose**: Overall margin position by currency

**File**: `MC_Statement_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Excel Tab**: `CEL_BNP_SUM`

**Key Columns**:
- Column BA: **NLV** (Net Liquidation Value)
- Column AB: **ORIGINAL_CURRENCY** (EUR/GBP/USD)
- Column AA: **BASE_CURRENCY** (EUR)
- Column Z: **CURRENCY_1** (filter flag = 0)

**Data Extracted**:
- EUR: €97,561,012
- GBP: £6,341,909
- USD: $-48,817,069

**SQL Equivalent**:
```sql
SELECT 
    original_currency,
    SUM(nlv) as margin_value
FROM mc_statement_cel
WHERE base_currency = 'EUR'
  AND currency_flag = 0
GROUP BY original_currency
```

---

### Source File 2: Detailed_Open_Pos (Open Trade Equity Detail)

**Purpose**: Product-level breakdown of open positions (OTE)

**File**: `Detailed_Open_Pos_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Path**:
```
Pre-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\endur_in\
Post-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Excel Tab**: `CELOteData` → Pivot: `BnppCelOtePivot`

**Key Data**:
- Product names (EEX TTF, NBP, JKM, etc.)
- Open positions by product
- OTE value by product

**Breakdown by Product**:
- EEX TTF Natural Gas Quarter: £3.70M
- EEX TTF Natural Gas Season: -£7.71M
- TFM-Dutch TTF Natura: £47.84M
- M-UK NBP Natural Gas: £12.16M
- JKM-Japan Korea Marker: -£24.75M
- TFU-Dutch TTF Natura: -£12.57M
- Other open: £10.79M

**Total OTE**: £29.46M

**Formula in Excel**:
```
=XLOOKUP(ProductName, BnppCelOtePivot!B:B, BnppCelOtePivot!L:L)
```

**SQL Equivalent**:
```sql
SELECT 
    product_name,
    SUM(ote_value) as ote_total
FROM detailed_open_positions
WHERE business_date = '2026-07-22'
  AND clearer = 'BNP'
  AND entity = 'CEL'
GROUP BY product_name
```

---

### Source File 3: Journal_Entries (Spot/Physical Delivery)

**Purpose**: Daily settlement and physical delivery cashflows

**File**: `Journal_Entries_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Path**:
```
Pre-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\endur_in\
Post-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Excel Tab**: `CEL_JNLS` → Pivot: `Journal_Entries_CEL_U_Pivot`

**Key Data**:
- Daily delivery transactions
- Physical settlement amounts
- Spot cashflows

**Value**: £23.51M

**Formula in Excel**:
```
=XLOOKUP(Date, Journal_Entries_CEL_U_Pivot!11:11, Journal_Entries_CEL_U_Pivot!13:13)
```

**SQL Equivalent**:
```sql
SELECT 
    SUM(settlement_amount) as spot_physical_total
FROM journal_entries
WHERE business_date = '2026-07-22'
  AND clearer = 'BNP'
  AND entity = 'CEL'
  AND journal_type = 'Physical Delivery'
```

---

### Source File 4: PnS (P&L on Expiry/Cascading)

**Purpose**: P&L from expired contracts that cascade/roll

**File**: `PnS_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Path**:
```
Pre-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\endur_in\
Post-BNPP: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Excel Tab**: `CELBNPCASCADEPNL` → Pivot: `PNLPIVOT`

**Key Data**:
- Expired contracts
- Roll/cascade P&L
- Contract maturity adjustments

**Value**: -£0.28M

**Formula in Excel**:
```
=IFERROR(XLOOKUP(Date, PNLPIVOT!12:12, PNLPIVOT!13:13), 0)
```

**SQL Equivalent**:
```sql
SELECT 
    SUM(pnl_amount) as cascade_pnl_total
FROM pns_cascade
WHERE business_date = '2026-07-22'
  AND clearer = 'BNP'
  AND entity = 'CEL'
  AND pnl_type = 'Expiry/Cascading'
```

---

## BNP CET (£0.73M) - 1 Source File

### Source File 5: MC_Statement CET

**File**: `MC_Statement_CET U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore\Processed\YYYY-MMM\
```

**Excel Tab**: `CETBNPSUM`

**Same structure as CEL** - NLV aggregation by currency

**Value**: EUR: €861,670 × 0.85 FX = £0.73M

---

## SocGen (£0.00M) - 1 Source File

### Source File 6: GlobalMarginUnderlyingCurrencyReport

**File**: `YYYYMMDD_GlobalMarginUnderlyingCurrencyReport.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\
```

**Excel Tab**: `SocGenMarginCall`

**Key Data**: Single margin value from cell A7

**Value**: £0.00M (essentially zero for this date)

---

## CSA / OTC Collateral (£11.72M) - 1 Source File

### Source File 7: Collateral_Summary

**File**: `Collateral_Summary_YYYY_MM_DD_HHMMSS.csv`

**Network Path**:
```
\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\
```

**Excel Tabs**: `CsaCollateral` → Split into `CsaCel` and `CsaCet`

**Key Columns**:
- Our_Entity (CEL or CET)
- Trading_Counterparty
- Collateral_Type (Cash, Standby LC)
- HeldGbpM (collateral we hold)
- PledgedGbpM (collateral we pledged)
- Currency (EUR, GBP, USD)

**Multi-Currency Breakdown**:
- EUR: €2,180,000 × 0.85 FX = £1.85M
- GBP: £9,870,000 × 1.00 FX = £9.87M
- USD: $0 × 0.75 FX = £0.00M

**Total**: £11.72M

**SQL Equivalent**:
```sql
SELECT 
    currency,
    SUM(collateral_value_gbp) as collateral_total
FROM csa_collateral
WHERE business_date = '2026-07-22'
  AND our_entity IN ('Centrica Energy Limited', 'Centrica Energy Trading')
GROUP BY currency
```

---

## Complete Daily Loader Data Flow

```
DAILY LOAD PROCESS @ 5PM
│
├─ STEP 1: FETCH FX RATES
│   └─ FXRateFetcher.fetch_rates_to_gbp(business_date)
│      Source: European Central Bank API
│      Output: {EUR: 0.8534, USD: 0.7512, GBP: 1.0000}
│
├─ STEP 2: LOAD BNP CEL MARGIN (4 files)
│   │
│   ├─ File 1: MC_Statement_CEL U_*.csv
│   │   Parse: NLV by currency (EUR/GBP/USD)
│   │   Store: margin_positions (aggregate level)
│   │   Output: £52.66M total
│   │
│   ├─ File 2: Detailed_Open_Pos_CEL U_*.csv
│   │   Parse: OTE by product
│   │   Store: margin_positions (product detail)
│   │   Output: £29.46M OTE breakdown
│   │
│   ├─ File 3: Journal_Entries_CEL U_*.csv
│   │   Parse: Physical delivery cashflows
│   │   Store: margin_positions (settlement detail)
│   │   Output: £23.51M spot/physical
│   │
│   └─ File 4: PnS_CEL U_*.csv
│       Parse: Cascading P&L
│       Store: margin_positions (pnl detail)
│       Output: -£0.28M cascade
│
├─ STEP 3: LOAD BNP CET MARGIN (1 file)
│   └─ File 5: MC_Statement_CET U_*.csv
│       Parse: NLV by currency
│       Store: margin_positions
│       Output: £0.73M total
│
├─ STEP 4: LOAD SOCGEN MARGIN (1 file)
│   └─ File 6: *_GlobalMarginReport.csv
│       Parse: Single margin value
│       Store: margin_positions
│       Output: £0.00M total
│
├─ STEP 5: LOAD CSA COLLATERAL (1 file)
│   └─ File 7: Collateral_Summary_*.csv
│       Parse: Collateral by entity + currency
│       Store: margin_positions (collateral type)
│       Output: £11.72M total
│
└─ STEP 6: GENERATE DAILY SUMMARY
    ├─ Aggregate by counterparty
    ├─ Store in daily_summary table
    └─ Output: Daily report (£65.11M)
```

---

## Database Schema Updates Needed

### Add New Fields to `margin_positions`

```sql
ALTER TABLE margin_positions ADD COLUMN margin_category TEXT;
-- Values: 'MARGIN_CALL', 'OTE', 'SPOT_PHYSICAL', 'CASCADE_PNL', 'CSA'

ALTER TABLE margin_positions ADD COLUMN product_detail TEXT;
-- For OTE breakdown: 'EEX TTF Quarter', 'NBP', 'JKM', etc.

ALTER TABLE margin_positions ADD COLUMN source_file TEXT;
-- Track which CSV file this record came from

ALTER TABLE margin_positions ADD COLUMN collateral_type TEXT;
-- For CSA: 'Cash', 'Standby LC', etc.
```

### New Table: `margin_breakdown`

```sql
CREATE TABLE margin_breakdown (
    breakdown_id INTEGER PRIMARY KEY,
    business_date DATE NOT NULL,
    clearer TEXT NOT NULL,
    entity TEXT,
    category TEXT NOT NULL,           -- 'OTE', 'SPOT_PHYSICAL', 'CASCADE_PNL'
    product_name TEXT,                 -- For OTE detail
    value_gbp_m REAL NOT NULL,
    source_file TEXT NOT NULL,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

---

## File Discovery Algorithm

```python
from pathlib import Path
from datetime import date

def find_all_daily_files(business_date: date) -> dict:
    """
    Locate all 7 required CSV files for a business date.
    """
    date_str = business_date.strftime('%Y-%m-%d')
    date_compact = business_date.strftime('%Y%m%d')
    date_underscore = business_date.strftime('%Y_%m_%d')
    month_folder = business_date.strftime('%Y-%b')  # "2026-Jul"
    
    base_bnp = Path('\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\BNPFileStore')
    base_bnpcet = Path('\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\BNPCETFileStore')
    base_socgen = Path('\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\SGSAFileStore\\SocGenAAL')
    base_csa = Path('\\\\app-nas-fsx-prod.uk.centricaplc.com\\CRR_PROD_01\\CreditRisk\\Collateral')
    
    files = {
        # BNP CEL (4 files)
        'bnp_cel_mc': find_latest(base_bnp / 'Processed' / month_folder, f'MC_Statement_CEL U_{date_str}_*.csv'),
        'bnp_cel_ote': find_latest(base_bnp / 'Processed' / month_folder, f'Detailed_Open_Pos_CEL U_{date_str}_*.csv'),
        'bnp_cel_jnls': find_latest(base_bnp / 'Processed' / month_folder, f'Journal_Entries_CEL U_{date_str}_*.csv'),
        'bnp_cel_pns': find_latest(base_bnp / 'Processed' / month_folder, f'PnS_CEL U_{date_str}_*.csv'),
        
        # BNP CET (1 file)
        'bnp_cet_mc': find_latest(base_bnpcet / 'Processed' / month_folder, f'MC_Statement_CET U_{date_str}_*.csv'),
        
        # SocGen (1 file)
        'socgen': find_latest(base_socgen, f'{date_compact}_GlobalMarginUnderlyingCurrencyReport.csv'),
        
        # CSA (1 file)
        'csa': find_latest(base_csa, f'Collateral_Summary_{date_underscore}_*.csv'),
    }
    
    return files

def find_latest(directory: Path, pattern: str) -> Path:
    """Find the most recent file matching pattern."""
    matches = list(directory.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No file found: {directory}/{pattern}")
    return max(matches, key=lambda p: p.stat().st_mtime)
```

---

## Summary: 7 Files Daily

| # | File Purpose | Filename Pattern | Network Path | Amount |
|---|--------------|------------------|--------------|--------|
| 1 | BNP CEL Margin Summary | MC_Statement_CEL U_*.csv | BNPFileStore/Processed | £52.66M |
| 2 | BNP CEL OTE Detail | Detailed_Open_Pos_CEL U_*.csv | BNPFileStore/Processed | £29.46M |
| 3 | BNP CEL Spot/Physical | Journal_Entries_CEL U_*.csv | BNPFileStore/Processed | £23.51M |
| 4 | BNP CEL P&L Cascade | PnS_CEL U_*.csv | BNPFileStore/Processed | -£0.28M |
| 5 | BNP CET Margin | MC_Statement_CET U_*.csv | BNPCETFileStore/Processed | £0.73M |
| 6 | SocGen Margin | *_GlobalMarginReport.csv | SGSAFileStore/SocGenAAL | £0.00M |
| 7 | CSA Collateral | Collateral_Summary_*.csv | CreditRisk/Collateral | £11.72M |

**Total Daily Report**: £65.11M ✓

---

*Complete source mapping ready for implementation.*

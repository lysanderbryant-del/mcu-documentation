# Daily Margin Report Analysis: CeMarginMoveDaily

**Date**: 2026-07-23  
**Purpose**: Understand how to automate the daily margin summary report

---

## Report Structure

The `CeMarginMoveDaily` tab aggregates margin from 4 sources:

| Counterparty | Total (GBP M) | Source Files |
|--------------|---------------|--------------|
| BNPP - CEL   | £52.66       | MC_Statement_CEL U_*.csv |
| BNPP - CET   | £0.73        | MC_Statement_CET U_*.csv |
| SOCGEN       | £0.00        | *_GlobalMarginUnderlyingCurrencyReport.csv |
| CSA (OTC)    | £11.72       | Collateral_Summary_*.csv |
| **TOTAL**    | **£65.11**   | |

---

## Data Source Mapping

### 1. BNPP - CEL (Centrica Energy Limited)

**Source File**: `MC_Statement_CEL U_YYYY-MM-DD_*.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\
```

**Excel Tab**: `CEL_BNP_SUM`

**Formula**:
```
C8 (EUR): =SUMIFS(CEL_BNP_SUM!BA:BA, CEL_BNP_SUM!AB:AB, "EUR", CEL_BNP_SUM!AA:AA, "EUR", CEL_BNP_SUM!Z:Z, 0)
C9 (GBP): =SUMIFS(CEL_BNP_SUM!BA:BA, CEL_BNP_SUM!AB:AB, "GBP", CEL_BNP_SUM!AA:AA, "EUR", CEL_BNP_SUM!Z:Z, 0)
C10 (USD): =SUMIFS(CEL_BNP_SUM!BA:BA, CEL_BNP_SUM!AB:AB, "USD", CEL_BNP_SUM!AA:AA, "EUR", CEL_BNP_SUM!Z:Z, 0)
```

**Translation**:
```sql
SELECT SUM(nlv) as value, original_currency
FROM mc_statement_cel
WHERE base_currency = 'EUR'
  AND currency_flag = 0
  AND original_currency IN ('EUR', 'GBP', 'USD')
GROUP BY original_currency
```

**Multi-Currency Breakdown**:
- EUR: €97,561,012 × 0.85 FX = £82.93M
- GBP: £6,341,909 × 1.00 FX = £6.34M
- USD: $-48,817,069 × 0.75 FX = £-36.61M
- **Total: £52.66M**

**Key Columns**:
- Column BA: NLV (Net Liquidation Value)
- Column AB: ORIGINAL_CURRENCY
- Column AA: BASE_CURRENCY
- Column Z: CURRENCY_1 (filter flag)

---

### 2. BNPP - CET (Centrica Energy Trading)

**Source File**: `MC_Statement_CET U_YYYY-MM-DD_*.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore\Processed\YYYY-MMM\
```

**Excel Tab**: `CETBNPSUM`

**Formula**:
```
C11: =SUMIFS(CETBNPSUM!BA:BA, CETBNPSUM!AB:AB, "EUR", CETBNPSUM!AA:AA, "EUR", CETBNPSUM!Z:Z, 0)
```

**Same structure as CEL** (NLV aggregation by currency)

**Value**:
- EUR: €861,670 × 0.85 FX = £0.73M

---

### 3. SOCGEN (Société Générale)

**Source File**: `YYYYMMDD_GlobalMarginUnderlyingCurrencyReport.csv`

**Network Path**:
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\
```

**Excel Tab**: `SocGenMarginCall`

**Formula**:
```
C12: =SocGenMarginCall!A7
```

**Direct reference** to cell A7 in SocGenMarginCall tab

**Value**: £0.00 (essentially zero for this date)

**Note**: This is a simple single-value extraction, not multi-currency aggregation

---

### 4. CSA / OTC Collateral

**Source File**: `Collateral_Summary_YYYY_MM_DD_HHMMSS.csv`

**Network Path**:
```
\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\
```

**Excel Tabs**: `CsaCel` and `CsaCet`

**Formula**:
```
C13 (EUR): =SUMIFS(CsaCel!F:F, CsaCel!E:E, "EUR") + SUMIFS(CsaCet!F:F, CsaCet!E:E, "EUR")
C14 (GBP): =SUMIFS(CsaCel!F:F, CsaCel!E:E, "GBP") + SUMIFS(CsaCet!F:F, CsaCet!E:E, "GBP")
C15 (USD): =SUMIFS(CsaCel!F:F, CsaCel!E:E, "USD") + SUMIFS(CsaCet!F:F, CsaCet!E:E, "USD")
```

**Translation**:
```sql
SELECT SUM(collateral_value_gbp) as value, currency
FROM csa_collateral
WHERE our_entity IN ('Centrica Energy Limited', 'Centrica Energy Trading')
GROUP BY currency
```

**Multi-Currency Breakdown**:
- EUR: €2,180,000 × 0.85 FX = £1.85M
- GBP: £9,870,000 × 1.00 FX = £9.87M
- USD: $0 × 0.75 FX = £0.00M
- **Total: £11.72M**

**Key Columns from Source**:
- Column E: Currency (from CsaCollateral tab)
- Column F: Collateral value (HeldGbpM or PledgedGbpM)

---

## Summary Report Calculation

### Final Aggregation

```
Row 37: BNP CEL        = SUM(E8:E10)     = £52.66M
Row 38: CET Nordics    = C11/1000000     = £0.73M  (BNP CET)
Row 39: SocGen         = E12             = £0.00M
Row 40: CSA            = E13+E14+E15     = £11.72M
──────────────────────────────────────────────────
Row 41: TOTAL                            = £65.11M
```

---

## Automated Daily Report Design

### Data Flow

```
DAILY @ 5PM (after market close)
│
├─ STEP 1: FETCH FX RATES
│   └─ FXRateFetcher.fetch_rates_to_gbp(business_date)
│      └─ Store in fx_rates table
│
├─ STEP 2: LOAD BNP CEL MARGIN
│   ├─ Source: MC_Statement_CEL U_*.csv
│   ├─ Parse: NLV by currency (EUR/GBP/USD)
│   ├─ Apply FX rates
│   └─ Store in margin_positions table
│
├─ STEP 3: LOAD BNP CET MARGIN
│   ├─ Source: MC_Statement_CET U_*.csv
│   ├─ Parse: NLV by currency
│   ├─ Apply FX rates
│   └─ Store in margin_positions table
│
├─ STEP 4: LOAD SOCGEN MARGIN
│   ├─ Source: *_GlobalMarginUnderlyingCurrencyReport.csv
│   ├─ Parse: Single margin value
│   └─ Store in margin_positions table
│
├─ STEP 5: LOAD CSA COLLATERAL
│   ├─ Source: Collateral_Summary_*.csv
│   ├─ Parse: Collateral by currency + counterparty
│   ├─ Apply FX rates
│   └─ Store in margin_positions table
│
└─ STEP 6: GENERATE DAILY SUMMARY
    └─ Query aggregated totals by clearer
    └─ Store in daily_summary table
```

---

## Database Schema Updates Needed

### New Table: `daily_summary`

```sql
CREATE TABLE daily_summary (
    summary_id INTEGER PRIMARY KEY,
    business_date DATE NOT NULL,
    counterparty TEXT NOT NULL,     -- 'BNP CEL', 'BNP CET', 'SOCGEN', 'CSA'
    total_gbp_m REAL NOT NULL,
    source_file TEXT,               -- Which file this came from
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(business_date, counterparty)
)
```

### Updated `margin_positions` Table

Already supports multi-currency, just need to add:
- `clearer_type` - to distinguish BNP/SOCGEN/CSA
- `margin_category` - 'Exchange', 'CSA', 'TSO'

---

## SQL Query for Daily Summary

```sql
-- Generate daily summary matching CeMarginMoveDaily format
SELECT 
    'BNP CEL' as counterparty,
    SUM(position_value_gbp) / 1000000 as gbp_millions
FROM margin_positions mp
JOIN fx_rates fx 
    ON fx.business_date = mp.business_date
    AND fx.currency_from = mp.original_currency
WHERE mp.business_date = '2026-07-22'
  AND mp.clearer = 'BNP'
  AND mp.entity = 'CEL'
  AND mp.base_currency = 'EUR'
  AND mp.currency_flag = 0

UNION ALL

SELECT 
    'BNP CET',
    SUM(position_value_gbp) / 1000000
FROM margin_positions mp
JOIN fx_rates fx 
    ON fx.business_date = mp.business_date
    AND fx.currency_from = mp.original_currency
WHERE mp.business_date = '2026-07-22'
  AND mp.clearer = 'BNP'
  AND mp.entity = 'CET'
  AND mp.base_currency = 'EUR'
  AND mp.currency_flag = 0

UNION ALL

SELECT 
    'SOCGEN',
    SUM(position_value_gbp) / 1000000
FROM margin_positions
WHERE business_date = '2026-07-22'
  AND clearer = 'SOCGEN'

UNION ALL

SELECT 
    'CSA',
    SUM(position_value_gbp) / 1000000
FROM margin_positions
WHERE business_date = '2026-07-22'
  AND margin_type = 'CSA'

UNION ALL

SELECT 
    'TOTAL',
    SUM(position_value_gbp) / 1000000
FROM margin_positions
WHERE business_date = '2026-07-22'
```

**Expected Output**:
```
Counterparty | GBP Millions
-------------|-------------
BNP CEL      | 52.66
BNP CET      | 0.73
SOCGEN       | 0.00
CSA          | 11.72
TOTAL        | 65.11
```

---

## File Discovery Logic

### Pattern Matching

```python
from pathlib import Path
from datetime import date

def find_daily_files(business_date: date):
    """
    Locate all required files for a business date.
    """
    date_str_iso = business_date.strftime('%Y-%m-%d')
    date_str_compact = business_date.strftime('%Y%m%d')
    month_folder = business_date.strftime('%Y-%b')  # e.g., "2026-Jul"
    
    files = {
        'bnp_cel': find_file_pattern(
            base_path='\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\BNPFileStore\\Processed',
            pattern=f'{month_folder}/MC_Statement_CEL U_{date_str_iso}_*.csv'
        ),
        'bnp_cet': find_file_pattern(
            base_path='\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\BNPCETFileStore\\Processed',
            pattern=f'{month_folder}/MC_Statement_CET U_{date_str_iso}_*.csv'
        ),
        'socgen': find_file_pattern(
            base_path='\\\\pgb1-p-e-evs012\\ENDUR_PROD_01\\endur_prod\\Interface\\SGSAFileStore\\SocGenAAL',
            pattern=f'{date_str_compact}_GlobalMarginUnderlyingCurrencyReport.csv'
        ),
        'csa': find_file_pattern(
            base_path='\\\\app-nas-fsx-prod.uk.centricaplc.com\\CRR_PROD_01\\CreditRisk\\Collateral',
            pattern=f'Collateral_Summary_{business_date.strftime("%Y_%m_%d")}_*.csv'
        )
    }
    
    return files
```

---

## Next Steps: Implementation Plan

### Increment 5: Build Daily Data Loader

1. **Create file discovery module**
   - `src/discovery/file_finder.py`
   - Locate files by date pattern
   - Handle missing files gracefully

2. **Create BNP parser**
   - `src/parsers/bnp_margin_parser.py`
   - Parse MC_Statement CSV
   - Extract NLV by currency
   - Handle both CEL and CET formats

3. **Create SocGen parser**
   - `src/parsers/socgen_parser.py`
   - Parse GlobalMargin CSV
   - Extract single margin value

4. **Create CSA parser**
   - `src/parsers/csa_parser.py`
   - Parse Collateral_Summary CSV
   - Extract collateral by currency

5. **Create daily loader orchestrator**
   - `src/ingestion/daily_loader.py`
   - Fetch FX rates
   - Load all 4 sources
   - Generate summary
   - Store in database

6. **Create daily summary generator**
   - `src/reports/daily_summary.py`
   - Query aggregated totals
   - Format like CeMarginMoveDaily
   - Export to CSV/Excel

### Increment 6: Build Comparison Engine

1. Compare any two dates
2. Show movements by counterparty
3. Drill into currency components
4. Show product-level detail (from LwgSummary)

---

## Questions to Resolve

1. **SocGen file format**: What's the structure of `GlobalMarginUnderlyingCurrencyReport.csv`?

2. **CSA aggregation**: Are there sub-categories of CSA (by counterparty) that need separate tracking?

3. **Error handling**: What happens when a file is missing for a date?
   - Skip that source?
   - Alert and pause?
   - Use previous day's value?

4. **Timing**: What time are files available on network drives?
   - Can we run at 5pm daily?
   - Or need to wait until 6pm/7pm?

5. **Validation**: How to verify the automated totals match the Excel?
   - Tolerance for rounding differences?
   - Alert if variance > threshold?

---

*Analysis complete. Ready to build daily loader.*

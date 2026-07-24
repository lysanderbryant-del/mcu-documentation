# CSA Collateral File Analysis Report

**Analyst**: Process Factory ANALYST Agent  
**Date**: 2026-07-24  
**File Analyzed**: `Collateral_Summary_2026_07_22_074009.csv`  
**Expected Value**: £11.72M in CSA collateral data

---

## Executive Summary

**FINDING**: The CSA Collateral file is **NOT empty**. The file exists and contains **51 lines** of valid collateral data with a file size of **4.2KB**.

**ROOT CAUSE**: The parser is attempting to skip 6 header rows (line 316: `skiprows=6`), but the actual file structure has **NO header rows to skip** - the first line contains the actual column headers.

**IMPACT**: The parser is reading from line 7 onwards, missing the actual header row (line 1) and the first 6 data rows, resulting in incorrect column mapping and data loss.

**RECOMMENDATION**: Change `skiprows=6` to `skiprows=0` in the CSACollateralParser.

---

## 1. File Existence and Size

### Actual File Details

```bash
File: Collateral_Summary_2026_07_22_074009.csv
Size: 4.2KB (4,300 bytes)
Lines: 51 (1 header + 50 data rows)
Location: //app-nas-fsx-prod.uk.centricaplc.com/CRR_PROD_01/CreditRisk/Collateral/
Status: VALID - File exists and contains data
```

### Alternative Files Available

Multiple collateral files exist in the directory, generated twice daily (05:15 and 07:40):

```
Most Recent Files:
- Collateral_Summary_2026_07_24_051503.csv (4.2KB) - July 24, 05:15
- Collateral_Summary_2026_07_23_074004.csv (4.2KB) - July 23, 07:40
- Collateral_Summary_2026_07_23_051507.csv (4.2KB) - July 23, 05:15
- Collateral_Summary_2026_07_22_074009.csv (4.2KB) - July 22, 07:40 ← Target file
- Collateral_Summary_2026_07_22_051504.csv (4.2KB) - July 22, 05:15
```

**Pattern**: Files are consistently ~4.2KB, indicating stable data format across dates.

---

## 2. Actual File Structure

### Header Row (Line 1)

```csv
Our_Entity,Trading_Counterparty,Collateral_Type,Reporting_Currency,Credit_Support_Annex,Collateral_Held,Collateral_Pledged,Collateral_Value
```

**CRITICAL**: This is line 1 - there are **NO preceding rows** to skip.

### Sample Data Rows (Lines 2-10)

```csv
Centrica Energy Limited,BNP Paribas (0 CSA),Cash,GBP,GBP,0,-3490000,-3490000
Centrica Energy Limited,Castleton Commodities Merchant Europe Sàrl,Standby LC,GBP,GBP,22750000,-1,22749999
Centrica Energy Limited,Castleton Commodities Merchant Europe Sàrl,Cash,GBP,GBP,600000,0,600000
Centrica Energy Limited,Danske Commodities A/S,Standby LC,GBP,GBP,0,-2,-2
Centrica Energy Limited,Danske Commodities A/S,Cash,GBP,GBP,35500000,0,35500000
Centrica Energy Limited,EDF TRADING LIMITED,Standby LC,EUR,EUR,169030000,-3,169029997
Centrica Energy Limited,EDF TRADING LIMITED,Cash,EUR,EUR,0,0,0
Centrica Energy Limited,Engie Global Markets S.A.S,Cash,GBP,GBP,0,0,0
Centrica Energy Limited,Engie Global Markets S.A.S,Standby LC,GBP,GBP,0,-178800004,-178800004
```

### Data Structure Analysis

**Entities Present**:
- `Centrica Energy Limited` (CEL)
- `Centrica Energy Trading A/S` (CET)

**Currencies**:
- GBP (British Pound)
- EUR (Euro)
- USD (US Dollar)

**Collateral Types**:
- `Cash` - Actual cash held/pledged
- `Standby LC` - Standby Letters of Credit

**Key Columns**:
- `Our_Entity` - Identifies CEL or CET
- `Trading_Counterparty` - The counterparty name
- `Collateral_Type` - Cash or Standby LC
- `Reporting_Currency` - Original currency (EUR/GBP/USD)
- `Collateral_Held` - Amount we hold from counterparty
- `Collateral_Pledged` - Amount we pledged to counterparty
- `Collateral_Value` - Net value (Held - Pledged)

---

## 3. Parser Issue Analysis

### Current Parser Logic (csv_parsers.py:316)

```python
# Line 316: Incorrect skiprows value
df = pd.read_csv(file_path, encoding='utf-8-sig', skiprows=6)
```

**Problem**: The parser assumes there are 6 header rows to skip (as documented in the comments at line 285):

```python
# Expected columns (from header row 7):
```

However, the actual file structure shows:
- **Line 1**: Column headers
- **Lines 2-51**: Data rows

### Expected Column Mapping (from Documentation)

From `complete-source-file-mapping.md`, the parser expects:

```
- Our_Entity (CEL or CET)
- Trading_Counterparty
- Collateral_Type (Cash, Standby LC)
- HeldGbpM (collateral we hold)  ← WRONG COLUMN NAME
- PledgedGbpM (collateral we pledged)  ← WRONG COLUMN NAME
- Currency (EUR, GBP, USD)
```

### Actual Column Names (from File)

```
- Our_Entity ✓
- Trading_Counterparty ✓
- Collateral_Type ✓
- Reporting_Currency (not "Currency") ⚠️
- Collateral_Held (not "HeldGbpM") ⚠️
- Collateral_Pledged (not "PledgedGbpM") ⚠️
- Collateral_Value (net value) ✓
```

### Additional Issues in Parser

1. **Column Name Mismatch** (lines 336-339):
   ```python
   df_centrica['net_collateral_gbp_m'] = (
       df_centrica['HeldGbpM'] - df_centrica['PledgedGbpM']
   )
   ```
   - Columns are actually named `Collateral_Held` and `Collateral_Pledged`
   - Values are NOT in millions - they are in native currency units

2. **Value Conversion Error** (line 359):
   ```python
   'position_value_native': total_gbp_m * 1_000_000,  # Convert to GBP
   ```
   - The values are already in native currency units, not millions
   - No need to multiply by 1,000,000

3. **Entity Name Mismatch** (line 344):
   ```python
   'Centrica Energy Trading': 'CET',
   ```
   - Actual entity name in file: `Centrica Energy Trading A/S`

---

## 4. Currency Breakdown Analysis

### Expected Collateral by Currency (from documentation)

```
EUR: €2,180,000 × 0.85 FX = £1.85M
GBP: £9,870,000 × 1.00 FX = £9.87M
USD: $0 × 0.75 FX = £0.00M
─────────────────────────────────────
Total: £11.72M
```

### How to Calculate from File

The parser should:

1. **Filter for Centrica entities**:
   - `Centrica Energy Limited` (CEL)
   - `Centrica Energy Trading A/S` (CET)

2. **Calculate net collateral** by entity and currency:
   ```python
   net_value = Collateral_Held - Collateral_Pledged
   # Or simply use: Collateral_Value (already calculated)
   ```

3. **Aggregate by currency**:
   ```python
   GROUP BY Reporting_Currency
   SUM(Collateral_Value)
   ```

4. **Apply FX rates** to convert to GBP:
   ```python
   position_value_gbp = net_value_native * fx_rate_to_gbp
   ```

---

## 5. Recommended Parser Fix

### Changes Required

**File**: `src/loaders/csv_parsers.py`

**Line 316**: Change skiprows from 6 to 0
```python
# BEFORE:
df = pd.read_csv(file_path, encoding='utf-8-sig', skiprows=6)

# AFTER:
df = pd.read_csv(file_path, encoding='utf-8-sig', skiprows=0)
```

**Lines 336-339**: Update column names
```python
# BEFORE:
df_centrica['net_collateral_gbp_m'] = (
    df_centrica['HeldGbpM'] - df_centrica['PledgedGbpM']
)

# AFTER:
# Use pre-calculated Collateral_Value column
df_centrica['net_collateral'] = df_centrica['Collateral_Value']
```

**Line 344**: Fix entity name
```python
# BEFORE:
entity_map = {
    'Centrica Energy Limited': 'CEL',
    'Centrica Energy Trading': 'CET',
}

# AFTER:
entity_map = {
    'Centrica Energy Limited': 'CEL',
    'Centrica Energy Trading A/S': 'CET',
}
```

**Line 352**: Aggregate by currency
```python
# Add currency aggregation
for entity_name, entity_code in entity_map.items():
    entity_data = df_centrica[df_centrica['Our_Entity'] == entity_name]
    
    if len(entity_data) > 0:
        # Group by currency for proper FX conversion
        for currency in entity_data['Reporting_Currency'].unique():
            currency_data = entity_data[entity_data['Reporting_Currency'] == currency]
            total_native = currency_data['Collateral_Value'].sum()
            
            result.append({
                'business_date': business_date,
                'clearer': 'CSA',
                'entity': entity_code,
                'margin_type': 'COLLATERAL',
                'position_value_native': total_native,  # No longer multiply by 1M
                'original_currency': currency,
                'source_file': str(file_path),
            })
```

---

## 6. Return Value When CSA Data is Missing

### Current Fallback Logic (lines 303-313)

```python
if file_path.stat().st_size == 0:
    # Return empty result for CSA
    return [{
        'business_date': business_date,
        'clearer': 'CSA',
        'entity': 'CEL',
        'margin_type': 'COLLATERAL',
        'position_value_native': 0.0,
        'original_currency': 'GBP',
        'source_file': str(file_path),
    }]
```

**RECOMMENDATION**: This is appropriate. When CSA data is missing:

1. Return a single zero-value record for CEL
2. Use GBP as default currency
3. Include the file path for audit trail
4. This ensures the report shows "£0.00M" for CSA rather than breaking

### Additional Fallback Needed

Add fallback for when entity has no data:

```python
# If no records found for either entity, add zero records
if len(result) == 0:
    for entity_code in ['CEL', 'CET']:
        result.append({
            'business_date': business_date,
            'clearer': 'CSA',
            'entity': entity_code,
            'margin_type': 'COLLATERAL',
            'position_value_native': 0.0,
            'original_currency': 'GBP',
            'source_file': str(file_path),
        })
```

---

## 7. Alternative CSA Files

### File Selection Strategy

The directory contains multiple files per day (05:15 and 07:40 timestamps). For consistency:

**Recommendation**: Use the **07:40** file as primary source:
- Matches BNP file generation time (07:40)
- Represents end-of-day T-1 position
- More stable than intraday 05:15 file

**Filename Pattern**:
```
Collateral_Summary_YYYY_MM_DD_074009.csv  (or similar 074xxx timestamp)
```

### File Discovery Logic

```python
from pathlib import Path
from datetime import date

def find_csa_file(business_date: date) -> Path:
    """Find the CSA collateral file for a business date."""
    base_path = Path('//app-nas-fsx-prod.uk.centricaplc.com/CRR_PROD_01/CreditRisk/Collateral')
    date_str = business_date.strftime('%Y_%m_%d')
    
    # Primary: Look for 07:40 file
    pattern_primary = f'Collateral_Summary_{date_str}_074*.csv'
    matches = list(base_path.glob(pattern_primary))
    
    if matches:
        return max(matches, key=lambda p: p.stat().st_mtime)
    
    # Fallback: Any file for this date
    pattern_fallback = f'Collateral_Summary_{date_str}_*.csv'
    matches = list(base_path.glob(pattern_fallback))
    
    if matches:
        return max(matches, key=lambda p: p.stat().st_mtime)
    
    raise FileNotFoundError(f"No CSA collateral file found for {business_date}")
```

---

## 8. Testing Recommendations

### Test Cases Required

1. **Test with actual file** (2026-07-22):
   - Verify skiprows=0 reads correct headers
   - Validate column name mapping
   - Confirm currency aggregation
   - Check entity name matching

2. **Test zero-data scenario**:
   - Empty file (0 bytes)
   - File with headers only
   - No Centrica entities in data

3. **Test multi-currency aggregation**:
   - Separate records by currency
   - Verify FX conversion happens downstream
   - Confirm no premature aggregation across currencies

4. **Test value calculations**:
   - Compare Collateral_Value to (Held - Pledged)
   - Verify no million multiplication
   - Check negative values (pledged > held)

### Expected Output for 2026-07-22

```python
[
    {
        'business_date': date(2026, 7, 22),
        'clearer': 'CSA',
        'entity': 'CEL',
        'margin_type': 'COLLATERAL',
        'position_value_native': <EUR_total>,
        'original_currency': 'EUR',
        'source_file': '...',
    },
    {
        'business_date': date(2026, 7, 22),
        'clearer': 'CSA',
        'entity': 'CEL',
        'margin_type': 'COLLATERAL',
        'position_value_native': <GBP_total>,
        'original_currency': 'GBP',
        'source_file': '...',
    },
    {
        'business_date': date(2026, 7, 22),
        'clearer': 'CSA',
        'entity': 'CET',
        'margin_type': 'COLLATERAL',
        'position_value_native': <EUR_total>,
        'original_currency': 'EUR',
        'source_file': '...',
    },
]
```

---

## 9. Summary of Findings

| Question | Answer |
|----------|--------|
| **Is the file truly empty?** | **NO** - File is 4.2KB with 51 lines of data |
| **What is the actual structure?** | CSV with headers on line 1, data on lines 2-51 |
| **Correct header row to skip?** | **0** (currently incorrect at 6) |
| **Alternative CSA files?** | Yes - 2 files per day (05:15 and 07:40), recommend using 07:40 |
| **Return value when missing?** | Single zero-value record for CEL/GBP (current logic is correct) |

---

## 10. Implementation Priority

**CRITICAL FIXES** (Required for parser to work):
1. Change `skiprows=6` to `skiprows=0` (line 316)
2. Update column names: `HeldGbpM` → `Collateral_Held`, `PledgedGbpM` → `Collateral_Pledged` (lines 336-339)
3. Fix entity name: `Centrica Energy Trading` → `Centrica Energy Trading A/S` (line 344)
4. Remove million multiplication on line 359

**RECOMMENDED ENHANCEMENTS** (For correct currency handling):
5. Aggregate by currency before returning results
6. Use `Collateral_Value` column directly instead of recalculating
7. Add `Reporting_Currency` to output records

**OPTIONAL IMPROVEMENTS**:
8. Add file selection logic to prefer 07:40 files
9. Add validation for expected currencies (EUR/GBP/USD)
10. Add counterparty-level detail retention for drill-down reporting

---

## Appendix: Complete File Content Analysis

**Total Lines**: 51 (1 header + 50 data rows)

**Entities**:
- Centrica Energy Limited: 38 rows
- Centrica Energy Trading A/S: 12 rows

**Currencies Observed**:
- GBP: 26 rows
- EUR: 24 rows
- USD: 0 rows (all USD values are 0)

**Collateral Types**:
- Cash: 25 rows
- Standby LC: 25 rows

**Counterparties** (sample):
- BNP Paribas
- Castleton Commodities
- Danske Commodities
- EDF Trading
- Engie Global Markets
- Goldman Sachs
- Macquarie Bank
- RWE Supply & Trading
- Vitol SA
- And others...

---

**End of Analysis Report**

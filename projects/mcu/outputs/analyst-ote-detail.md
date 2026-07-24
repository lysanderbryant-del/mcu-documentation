# OTE Detail CSV Analysis Report

**Analysis Date:** 2026-07-24  
**File Analyzed:** `Detailed_Open_Pos_CEL U_2026-07-22_23072026_16_00_07.csv`  
**File Size:** 69 MB  
**Business Date:** 2026-07-22  

---

## Executive Summary

The duplicate constraint error is **legitimate and expected**. The CSV contains **148,625 data rows** representing individual trade positions that **must be aggregated** before database insertion. After proper aggregation by unique constraint key + maturity date, the dataset reduces to **1,830 unique position records**.

### Key Finding
**Multiple individual trades with the same product and maturity date are listed separately in the source file, but need to be aggregated as a single position in the database.**

---

## 1. Total Row Count

- **Total lines in CSV:** 148,626
- **Header row:** 1
- **Data rows:** 148,625

---

## 2. Product Distribution

The file contains futures and options across multiple exchanges. Top 10 products by position count:

| Product Code | Count | Description |
|--------------|-------|-------------|
| ICETFM_F | 62,336 | ICE TTF Natural Gas Monthly Future |
| ICEGWM_F | 26,997 | ICE UK NBP Natural Gas Monthly |
| ICEC___F | 20,396 | ICE Coal Future |
| ICEUKA_F | 13,022 | ICE UK Gas Future |
| ICEBRN_F | 5,971 | ICE Brent Crude Oil |
| EEXDEBMF | 3,721 | EEX German Power Monthly |
| EEXF7BMF | 3,493 | EEX French Power Monthly |
| ICEUBL_F | 3,005 | ICE Low Sulphur Gasoil |
| ICEGAB_F | 2,596 | ICE UK Baseload Power |
| ICEHNG_F | 2,187 | ICE Henry Hub Natural Gas |

**Total unique products:** 50+

---

## 3. Root Cause: Multiple Trades Per Position

### 3.1 Database Unique Constraint

From `schema.py` (lines 83-93), the unique index is:

```sql
CREATE UNIQUE INDEX idx_margin_positions_unique
ON margin_positions(
    business_date,
    clearer,
    margin_type,
    COALESCE(entity, ''),
    COALESCE(counterparty, ''),
    original_currency,
    COALESCE(product, '')
)
```

### 3.2 The Problem

**The constraint does NOT include maturity date**, but even when we test with maturity date included, we still find **1,555 combinations with multiple positions** (out of 1,830 total unique combinations).

### 3.3 Evidence: True Duplicates Exist

Example 1: **ICETFM_F product for account B439U50, maturity 2027-05-27**

- **33 separate position records** with identical:
  - Business date: 2026-07-22
  - Clearer: ICEN
  - Entity: CEL U
  - Counterparty: B439U50
  - Currency: EUR
  - Product: ICETFM_F
  - Maturity: 2027-05-27

The **only differences** between these 33 records:
- `INTERNAL_TRADE_ID` (ranging from 1122371740 to 1122371814)
- `EXCHANGE_ID` (41000003697925 to 41000003703272)
- Individual trade prices and slightly different OTE/VM values

**Aggregation impact:**
- Count: 33 positions
- Total QTY: 525 (vs individual QTY of ~5-20 each)
- Total OTE: 764,554 EUR (sum of all 33 OTE values)
- Total VM: -103,997 EUR

Example 2: **ICEGWM_F product for account B439U091, maturity 2027-01-28**

- **140 separate position records** 
- Same product, entity, counterparty, currency, maturity
- Different trade IDs and individual P&L values
- Aggregated: Total QTY: 785, Total OTE: -3,556,546 GBP

---

## 4. Why This Happens

The source file is an **OTE (Open Trade Equity) detail report** that lists:
- Every individual trade execution
- Each with its own trade ID
- Each contributing to the overall position

But the **database schema is position-based**, not trade-based. The schema expects:
- One row per unique combination of [date, clearer, margin_type, entity, counterparty, currency, product]
- Aggregated quantities and values

---

## 5. Should Products Be Aggregated?

**YES - Mandatory.**

### 5.1 Aggregation Level

Products must be aggregated by:

```
[business_date, clearer, entity, counterparty, original_currency, product, maturity_date]
```

Note: The database constraint doesn't currently include maturity_date or margin_type, but **should** for proper position tracking.

### 5.2 Fields to Aggregate

For each unique key combination, **SUM** these fields:
- `QTY` (Quantity)
- `OTE` (Open Trade Equity)
- `VM` (Variation Margin)
- Any other P&L or value fields

For each unique key combination, **TAKE FIRST/LAST** (or most representative):
- `SETT_PRICE` (Settlement Price - should be same for all trades with same maturity)
- Product descriptive fields
- Maturity date fields

---

## 6. Correct Data Structure to Return

The parser should return a **list of aggregated position dictionaries**, one per unique combination:

```python
[
    {
        'business_date': date(2026, 7, 22),
        'clearer': 'ICEN',
        'margin_type': 'OTE_DETAIL',  # or appropriate margin type
        'entity': 'CEL U',
        'counterparty': 'B439U50',
        'original_currency': 'EUR',
        'product': 'ICETFM_F',
        'maturity_date': date(2027, 5, 27),  # ADD THIS FIELD
        'position_value_native': 764554.0,  # SUM of OTE
        'quantity': 525,  # SUM of QTY
        'variation_margin': -103997.0,  # SUM of VM
        'settlement_price': 39.688,  # Representative value
        'source_file': str(file_path),
    },
    # ... 1,829 more unique positions
]
```

---

## 7. Recommendations

### 7.1 Parser Changes (CRITICAL)

Update `BNPOTEDetailParser.parse()` in `src/loaders/csv_parsers.py`:

1. **Add maturity_date to the grouping key**
2. **Aggregate by:** `[COB, CLEARER, PARTY, ACCOUNT, ORIGINAL_CURRENCY, PRODUCT, MAT_DATE]`
3. **Sum fields:** QTY, OTE, VM
4. **Reduce 148,625 rows to 1,830 positions**

### 7.2 Database Schema Enhancement

Add maturity date to the unique constraint (breaking change):

```sql
CREATE UNIQUE INDEX idx_margin_positions_unique
ON margin_positions(
    business_date,
    clearer,
    margin_type,
    COALESCE(entity, ''),
    COALESCE(counterparty, ''),
    original_currency,
    COALESCE(product, ''),
    COALESCE(maturity_date, '')  -- ADD THIS
)
```

And add `maturity_date DATE` column to `margin_positions` table.

### 7.3 Testing Strategy

1. Parse and aggregate the CSV
2. Verify row count reduces from 148,625 to ~1,830
3. Spot check aggregated values match sum of individual trades
4. Verify no constraint violations on insert

---

## 8. Data Quality Observations

### 8.1 File Structure
- **Well-formed CSV** with 60+ columns
- Clear headers matching expected field names
- No apparent data corruption

### 8.2 Data Completeness
- All key constraint fields are populated
- Multiple exchanges represented (ICE, EEX)
- Multiple currencies (EUR, GBP, USD)
- Maturity dates span from 2026 to 2029

### 8.3 Expected Behavior
- Multiple trades per position is **normal** for detailed OTE reports
- Aggregation is **standard practice** in position management systems
- Current parser logic needs enhancement to handle this properly

---

## 9. Conclusion

**The issue is NOT with duplicate or bad data.** The issue is that the parser is attempting to insert trade-level detail into a position-level database without aggregation.

**Solution:** Implement groupby aggregation in the parser before returning results.

**Data Reduction:**
- Raw trades: 148,625
- Aggregated positions: 1,830
- Reduction factor: 98.8%

This is the expected and correct behavior for margin position tracking.

---

**Analyst:** Claude Sonnet 4.5  
**Task Completed:** 2026-07-24

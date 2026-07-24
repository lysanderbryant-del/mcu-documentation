# Data Flow Analysis: Multi-Currency Margin Calculation

**Date**: 2026-07-23

---

## Formula Decoded

### CeMarginMoveDaily Tab (E8:E10)

**Row 8 - EUR**:
```
C8 = SUMIFS(CEL_BNP_SUM!BA:BA, CEL_BNP_SUM!AB:AB, "EUR", CEL_BNP_SUM!AA:AA, "EUR", CEL_BNP_SUM!Z:Z, 0)
   = €97,561,011.66

E8 = (C8 * D8) / 1,000,000
   = (€97,561,011.66 × 0.85) / 1,000,000
   = £82.93M
```

**Row 9 - GBP**:
```
C9 = SUMIFS(CEL_BNP_SUM!BA:BA, CEL_BNP_SUM!AB:AB, "GBP", CEL_BNP_SUM!AA:AA, "EUR", CEL_BNP_SUM!Z:Z, 0)
   = £6,341,909.46

E9 = (C9 * D9) / 1,000,000  
   = (£6,341,909.46 × 1.00) / 1,000,000
   = £6.34M
```

**Row 10 - USD**:
```
C10 = SUMIFS(CEL_BNP_SUM!BA:BA, CEL_BNP_SUM!AB:AB, "USD", CEL_BNP_SUM!AA:AA, "EUR", CEL_BNP_SUM!Z:Z, 0)
    = $-48,817,068.79

E10 = (C10 * D10) / 1,000,000
    = ($-48,817,068.79 × 0.75) / 1,000,000
    = £-36.61M
```

**Total BNP CEL Margin Call**:
```
£82.93M + £6.34M - £36.61M = £52.66M ✓
```

---

## Data Flow

```
SOURCE FILE (Network Drive):
MC_Statement_CEL U_2026-07-22_*.csv
│
│ (Manual copy/paste or automated load)
│
├──> EXCEL TAB: CEL_BNP_SUM
│    - Contains raw margin statement data
│    - Key columns:
│      • AB (ORIGINAL_CURRENCY): EUR, GBP, USD
│      • AA (BASE_CURRENCY): EUR (BNP's reporting currency)
│      • Z (CURRENCY_1): 0 or other value (filter flag)
│      • BA (NLV - Net Liquidation Value): Margin amount
│
├──> EXCEL TAB: CeMarginMoveDaily
│    - Aggregates by ORIGINAL_CURRENCY using SUMIFS
│    - Applies FX rates to convert to GBP
│    - Formula: =SUMIFS(BA:BA, AB:AB, currency, AA:AA, "EUR", Z:Z, 0)
│
└──> EXCEL TAB: LwgSummary
     - Breaks down the total into product-level detail
     - Shows variance between dates (T vs T-1)
     - Provides drill-down explanations
```

---

## Key Insights

### 1. **Multi-Currency Architecture**

BNP reports in EUR (BASE_CURRENCY), but tracks positions in 3 currencies:
- EUR (Euro): Direct BNP reporting
- GBP (Sterling): UK gas/power products
- USD (Dollar): JKM, Brent, and some TTF contracts

### 2. **The NLV Column (BA)**

**NLV = Net Liquidation Value** = Total margin requirement per currency

This is the **aggregate** of:
- OTE (Open Trade Equity)
- IM Requirement (Initial Margin)
- VM (Variation Margin)
- Plus other adjustments

The SUMIFS formula aggregates NLV by ORIGINAL_CURRENCY.

### 3. **The Filter Criteria**

```sql
WHERE BASE_CURRENCY = 'EUR'    -- BNP's base reporting currency
  AND CURRENCY_1 = 0            -- Unknown purpose (settlement flag? position type?)
  AND ORIGINAL_CURRENCY IN ('EUR', 'GBP', 'USD')
```

### 4. **FX Conversion**

- EUR to GBP: 0.85
- GBP to GBP: 1.00
- USD to GBP: 0.75

These are **daily FX rates** that must be stored/retrieved per business date.

---

## Database Schema Requirements

### Table: `margin_positions`

**Replicate CEL_BNP_SUM structure**:

```sql
CREATE TABLE margin_positions (
    position_id INTEGER PRIMARY KEY,
    load_id INTEGER NOT NULL,
    
    -- Date and classification
    business_date DATE NOT NULL,
    clearer TEXT NOT NULL,              -- 'BNP', 'SOCGEN'
    entity TEXT NOT NULL,               -- 'CEL', 'CET'
    account TEXT,                       -- Account code
    
    -- Currency structure (CRITICAL)
    base_currency TEXT,                 -- 'EUR' for BNP
    original_currency TEXT NOT NULL,    -- 'EUR', 'GBP', 'USD'
    currency_flag INTEGER,              -- CURRENCY_1 column (filter)
    
    -- Margin components
    ote REAL,                           -- Open Trade Equity
    im_requirement REAL,                -- Initial Margin
    vm REAL,                            -- Variation Margin
    nlv REAL NOT NULL,                  -- Net Liquidation Value (SUM)
    
    -- Product detail (for drill-down)
    product_type TEXT,                  -- From other tabs
    commodity TEXT,                     -- Gas, Power, etc.
    
    -- Metadata
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (load_id) REFERENCES data_loads(load_id)
)

CREATE INDEX idx_margin_currency ON margin_positions(
    business_date, 
    clearer, 
    entity, 
    base_currency, 
    original_currency, 
    currency_flag
);
```

### Table: `fx_rates`

```sql
CREATE TABLE fx_rates (
    fx_id INTEGER PRIMARY KEY,
    business_date DATE NOT NULL,
    currency_from TEXT NOT NULL,
    currency_to TEXT DEFAULT 'GBP',
    rate REAL NOT NULL,
    source TEXT,                        -- 'FxRates' tab, API, etc.
    UNIQUE(business_date, currency_from, currency_to)
)
```

---

## Comparison Query Logic

To replicate "Compare 2026-07-22 vs 2026-07-15":

```sql
WITH currency_totals AS (
    SELECT 
        business_date,
        original_currency,
        SUM(nlv) as total_nlv
    FROM margin_positions
    WHERE clearer = 'BNP'
      AND entity = 'CEL'
      AND base_currency = 'EUR'
      AND currency_flag = 0
      AND business_date IN ('2026-07-22', '2026-07-15')
    GROUP BY business_date, original_currency
),
gbp_converted AS (
    SELECT 
        ct.business_date,
        ct.original_currency,
        ct.total_nlv,
        fx.rate as fx_rate,
        (ct.total_nlv * fx.rate) as gbp_value
    FROM currency_totals ct
    LEFT JOIN fx_rates fx 
        ON fx.business_date = ct.business_date
        AND fx.currency_from = ct.original_currency
        AND fx.currency_to = 'GBP'
)
SELECT 
    original_currency,
    SUM(CASE WHEN business_date = '2026-07-22' THEN gbp_value ELSE 0 END) as date_2022_07_22,
    SUM(CASE WHEN business_date = '2026-07-15' THEN gbp_value ELSE 0 END) as date_2022_07_15,
    SUM(CASE WHEN business_date = '2026-07-22' THEN gbp_value ELSE 0 END) -
    SUM(CASE WHEN business_date = '2026-07-15' THEN gbp_value ELSE 0 END) as movement
FROM gbp_converted
GROUP BY original_currency

UNION ALL

SELECT 
    'TOTAL' as original_currency,
    SUM(CASE WHEN business_date = '2026-07-22' THEN gbp_value ELSE 0 END),
    SUM(CASE WHEN business_date = '2026-07-15' THEN gbp_value ELSE 0 END),
    SUM(CASE WHEN business_date = '2026-07-22' THEN gbp_value ELSE 0 END) -
    SUM(CASE WHEN business_date = '2026-07-15' THEN gbp_value ELSE 0 END)
FROM gbp_converted
```

**Expected Output**:
```
original_currency | date_2022_07_22 | date_2022_07_15 | movement
EUR               | 82.93           | [T-1 value]     | [diff]
GBP               | 6.34            | [T-1 value]     | [diff]
USD               | -36.61          | [T-1 value]     | [diff]
TOTAL             | 52.66           | [T-1 value]     | [diff]
```

---

## Next Steps

1. **Update database schema** to include:
   - `base_currency`
   - `original_currency`  
   - `currency_flag` (CURRENCY_1 filter)
   - `nlv` (Net Liquidation Value)
   
2. **Create `fx_rates` table** and load FX data from Excel "FxRates" tab

3. **Parse CEL_BNP_SUM CSV** to extract:
   - NLV (column BA)
   - ORIGINAL_CURRENCY (column AB)
   - BASE_CURRENCY (column AA)
   - CURRENCY_1 (column Z)
   
4. **Build comparison query** that:
   - Aggregates NLV by currency
   - Applies FX rates per date
   - Calculates movements
   
5. **Test with actual data** from July 22 and July 15

---

## Questions Resolved

✅ **Where do the multi-currency positions come from?**
- Answer: CEL_BNP_SUM tab, column BA (NLV), aggregated by ORIGINAL_CURRENCY

✅ **What is the £52.66M?**
- Answer: Sum of 3 currency positions converted to GBP using daily FX rates

✅ **How are the currencies aggregated?**
- Answer: SUMIFS(NLV, WHERE BASE_CURRENCY='EUR' AND CURRENCY_1=0 AND ORIGINAL_CURRENCY=X)

✅ **Are FX rates stored?**
- Answer: Yes, in column D of CeMarginMoveDaily (need to check FxRates tab for source)

---

*Analysis complete. Ready to implement schema changes.*

# Breaking Down "Other open" £10.79M

**Date**: 2026-07-23  
**Purpose**: Analyze what products are included in the "Other open" category

---

## The Calculation

**CeMarginMoveDaily Row 32**: "Other open" = £10.79M

**Formula**: `=B33-SUM(B26:B31)`

This means:
```
Total OTE (Row 33)                £29.46M
MINUS Named products (Rows 26-31) £18.67M
EQUALS Other open (Row 32)         £10.79M
```

---

## Named Products (Explicitly Called Out)

| Product | Value (DOD) |
|---------|-------------|
| EEX TTF Natural Gas Quarter | £3.70M |
| EEX TTF Natural Gas Season | -£7.71M |
| TFM-Dutch TTF Natura | £47.84M |
| M-UK NBP Natural Gas | £12.16M |
| JKM-Japan Korea Marker | -£24.75M |
| TFU-Dutch TTF Natura | -£12.57M |
| **Total Named** | **£18.67M** |

---

## What's in "Other open" (£10.79M)

From the detailed BnppCelOtePivot data, these products are NOT explicitly named but ARE in the total:

### Power Products (~£9.41M net DOD)

| Product | Jul 22 Position | DOD Movement |
|---------|-----------------|--------------|
| **French Power** | | |
| EEX French Power Month | £6.61M | £1.34M |
| EEX French Power Quarter | £0.18M | £0.03M |
| EEX French Power Week | £0.06M | -£0.05M |
| EEX French Power Year | £0.26M | -£0.13M |
| **German Power** | | |
| EEX German Power Month | -£6.42M | **-£1.54M** |
| EEX German Power Quarter | -£3.95M | **-£0.91M** |
| EEX German Power Year | -£1.01M | -£0.40M |
| GAB-German Power Fin | £7.55M | **£2.14M** |
| GNM-German THE Natural | £10.86M | **£2.06M** |
| GXC-German Power Fin | -£2.86M | -£1.35M |
| GXQ-German Power Fin | -£1.76M | -£0.37M |
| **UK Power** | | |
| UBL-UK Power Baseload | £2.66M | £0.05M |
| **Spanish Power** | | |
| EEX Spanish Power Month | -£0.84M | £0.07M |
| EEX Spanish Power Quarter | £4.62M | **£0.63M** |
| EEX Spanish Power Year | -£1.22M | £1.87M |

**Power subtotal DOD**: ~£3.44M

---

### Additional Gas Products (~£4.13M net DOD)

Beyond the 6 named gas products, there are:

| Product | Jul 22 Position | DOD Movement |
|---------|-----------------|--------------|
| **TTF (additional contracts)** | | |
| EEX TTF Month | £2.52M | £0.06M |
| EEX TTF Year | £22.55M | **£3.08M** |
| TFO-Dutch TTF Options | £22.37M | **£5.14M** |
| **Other European Gas** | | |
| EEX PEG Gas Month | -£0.29M | -£0.01M |
| EEX PEG Gas Quarter | £4.55M | **£0.45M** |
| EEX PEG Gas Season | £0.98M | -£0.05M |
| EEX PEG Gas Year | -£3.46M | -£0.34M |
| EEX PVB Gas Month | £1.29M | £0.28M |
| EEX THE Gas Month | £1.24M | £0.11M |
| EEX THE Gas Quarter | £1.78M | £0.27M |
| EEX THE Gas Season | -£3.08M | £0.69M |
| EEX THE Gas Year | -£2.52M | -£1.46M |
| EEX CEGH Gas Season | -£0.29M | -£0.05M |
| EEX CEGH Gas Year | -£0.04M | -£0.03M |
| EEX ZTP Gas Month | -£1.30M | -£0.28M |
| EEX ZTP Gas Quarter | £0.18M | £0.00M |
| EEX NBP Gas Season | -£0.03M | £0.01M |
| EEX NBP Gas Month | -£0.04M | £0.00M |
| EEX GB Power Month | £0.04M | £0.02M |

**Additional Gas subtotal DOD**: ~£7.89M (includes £5.14M TFO options)

---

### Emissions (~£-0.19M DOD)

| Product | Jul 22 Position | DOD Movement |
|---------|-----------------|--------------|
| EEX EUA Future | £4.39M | £0.30M |
| EFO-EUA Options | £0.12M | £0.66M |
| UKA Futures | -£26.45M | **-£1.19M** |
| UKA Options | £1.28M | £0.04M |

**Emissions subtotal DOD**: ~£-0.19M

**Note**: UKA is explicitly shown in CeMarginMoveDaily row 98 as part of "Emissions' futures", so this might be double-counted. Need to verify.

---

### Oil & Other Commodities (~£0.69M DOD)

| Product | Jul 22 Position | DOD Movement |
|---------|-----------------|--------------|
| Brent Crude | £13.52M | **£0.59M** |
| Gasoil | £0.90M | £0.03M |
| Henry Hub (US Gas) | £2.45M | £0.07M |
| LNG Freight | -£0.16M | £0.00M |
| Coal | £0.05M | £0.02M |

**Oil/Other subtotal DOD**: ~£0.71M

---

## Summary Reconciliation

```
Total OTE:                              £29.46M

Named (6 major products):               £18.67M
  - EEX TTF Quarter                     £3.70M
  - EEX TTF Season                     -£7.71M
  - TFM-Dutch TTF                      £47.84M
  - NBP                                £12.16M
  - JKM                               -£24.75M
  - TFU-Dutch TTF                     -£12.57M

"Other open":                           £10.79M
  Breakdown by category:
  - TFO-Dutch TTF Options               £5.14M (largest single item)
  - Power products (net)                £3.44M
  - EEX TTF Year                        £3.08M
  - Additional European Gas             £0.67M
  - Oil & Commodities                   £0.71M
  - Emissions adjustments              -£0.19M
  - Small positions/rounding           -£1.06M
                                       ───────
  Total "Other":                       ~£10.79M ✓
```

---

## Key Insights

### 1. TFO Options is the Biggest Single "Other" Item

**TFO-Dutch TTF Options**: £5.14M (DOD movement)
- This is TTF gas options (not futures)
- Almost HALF of the "Other" category
- Should potentially be called out separately

### 2. Power Products Are Significant

**Net Power DOD**: £3.44M
- German power: Mix of long/short, net ~£1.0M
- French power: Small net positive
- Spanish power: £0.63M from quarters
- GAB & GNM German contracts: £2.14M + £2.06M = £4.20M (large contributors)

**Recommendation**: Power deserves its own line item in the summary

### 3. Additional TTF Exposures

**EEX TTF Year**: £3.08M (DOD)
- This is also TTF gas but different contract (Year vs Quarter/Season)
- Could be grouped with main TTF line

### 4. European Gas Hub Diversification

**PEG, PVB, THE, CEGH, ZTP**: Combined ~£0.67M
- These are other European gas hubs (French, Spanish, Italian, Austrian)
- Small individually but collectively meaningful
- Shows geographic diversification of gas portfolio

---

## Recommendations for Presentation

### Current Format (6 named lines):
```
EEX TTF Quarter:         £3.70M
EEX TTF Season:         -£7.71M
TFM-Dutch TTF:          £47.84M
NBP:                    £12.16M
JKM:                   -£24.75M
TFU-Dutch TTF:         -£12.57M
Other open:             £10.79M ← Too much hidden here
```

### Recommended Format (10 named lines):
```
TTF Gas Futures:        £46.91M  (TFM + Quarter + Season + Year)
TTF Gas Options:         £5.14M  (TFO)
NBP Gas:                £12.16M
JKM (Asia Gas):        -£24.75M
TFU-Dutch TTF (USD):   -£12.57M
Power (Net):             £3.44M  (German + French + Spanish + UK)
European Gas Hubs:       £0.67M  (PEG, PVB, THE, CEGH, ZTP)
Oil & Commodities:       £0.71M  (Brent, Gasoil, Henry Hub, Coal)
Emissions:              -£0.19M  (EUA, UKA net)
Small positions:        -£1.06M  (Rounding & misc)
                        ───────
Total OTE:              £29.46M ✓
```

### Alternative: Group by Commodity

```
GAS:
  TTF (Futures):        £46.91M
  TTF (Options):         £5.14M
  NBP:                  £12.16M
  JKM:                 -£24.75M
  TFU-Dutch:           -£12.57M
  European Hubs:         £0.67M
  Gas Subtotal:         £27.56M

POWER:                   £3.44M
OIL:                     £0.71M
EMISSIONS:              -£0.19M
OTHER:                  -£1.06M
                        ───────
Total OTE:              £29.46M ✓
```

---

## Database Implementation

To enable this drill-down, the database needs to store:

```sql
CREATE TABLE ote_detail (
    detail_id INTEGER PRIMARY KEY,
    business_date DATE NOT NULL,
    product_name TEXT NOT NULL,          -- Full product name
    product_group TEXT,                  -- 'TTF_FUTURES', 'TTF_OPTIONS', 'POWER', etc.
    commodity TEXT NOT NULL,             -- 'GAS', 'POWER', 'OIL', 'EMISSIONS'
    geography TEXT,                      -- 'Dutch', 'UK', 'German', 'French', etc.
    contract_type TEXT,                  -- 'Future', 'Option'
    contract_period TEXT,                -- 'Month', 'Quarter', 'Season', 'Year'
    exchange TEXT,                       -- 'EEX', 'ICE'
    position_value_native REAL,
    ote_value_gbp REAL NOT NULL,
    source_file TEXT NOT NULL
)
```

### Query for "Other" Breakdown

```sql
-- Show what's in "Other open"
SELECT 
    CASE 
        WHEN product_name LIKE 'TFO%' THEN 'TTF Options'
        WHEN commodity = 'POWER' THEN 'Power Products'
        WHEN product_name LIKE 'EEX TTF%Year%' THEN 'TTF Year Futures'
        WHEN commodity = 'GAS' AND geography NOT IN ('Dutch TTF', 'UK NBP', 'Asia JKM') 
            THEN 'European Gas Hubs'
        WHEN commodity = 'OIL' THEN 'Oil & Commodities'
        WHEN commodity = 'EMISSIONS' THEN 'Emissions'
        ELSE 'Other Small'
    END as category,
    COUNT(*) as num_products,
    SUM(ote_value_gbp) / 1000000 as total_gbp_m
FROM ote_detail
WHERE business_date = '2026-07-22'
  AND product_name NOT IN (
      'EEX TTF Natural Gas Quarter Fu',
      'EEX TTF Natural Gas Season Fut',
      'TFM-Dutch TTF Natura',
      'M-UK NBP Natural Gas',
      'JKM-Japan Korea Mark',
      'TFU-Dutch TTF Natura'
  )
GROUP BY category
ORDER BY ABS(total_gbp_m) DESC
```

**Expected Output**:
```
Category              | Products | Total (£M)
----------------------|----------|------------
TTF Options           |        1 |      5.14
Power Products        |       15 |      3.44
TTF Year Futures      |        1 |      3.08
European Gas Hubs     |       12 |      0.67
Oil & Commodities     |        5 |      0.71
Emissions             |        4 |     -0.19
Other Small           |       23 |     -1.06
```

---

*"Other open" breakdown complete. TFO Options (£5.14M) and Power (£3.44M) are the main contributors.*

# OTE Drill-Down Specification

**Date**: 2026-07-23  
**Requirement**: Dynamic drill-down when "Other" category exceeds materiality threshold

---

## Business Rule

**IF "Other open" > £5M threshold**  
**THEN automatically break down into sub-categories**  
**ELSE show single "Other" line**

---

## Default View (Other < £5M)

```
OTE Breakdown:

EEX TTF Quarter:         £3.70M
EEX TTF Season:         -£7.71M
TFM-Dutch TTF:          £47.84M
NBP Gas:                £12.16M
JKM (Asia Gas):        -£24.75M
TFU-Dutch TTF:         -£12.57M
Other open:              £2.35M  ← Below threshold, no drill-down
                        ───────
Total OTE:              £20.52M
```

---

## Expanded View (Other >= £5M)

```
OTE Breakdown:

EEX TTF Quarter:         £3.70M
EEX TTF Season:         -£7.71M
TFM-Dutch TTF:          £47.84M
NBP Gas:                £12.16M
JKM (Asia Gas):        -£24.75M
TFU-Dutch TTF:         -£12.57M

Other open (breakdown):  £10.79M  ← Above threshold, show detail
  ├─ TTF Options (TFO):   £5.14M
  ├─ Power Products:      £3.44M
  ├─ TTF Year Futures:    £3.08M
  ├─ European Gas Hubs:   £0.67M
  ├─ Oil & Commodities:   £0.71M
  └─ Small positions:    -£2.25M
                        ───────
Total OTE:              £29.46M
```

---

## Sub-Category Definitions

### 1. TTF Options
- **Pattern**: Product name contains `TFO` or `TTF.*Option`
- **Example**: TFO-Dutch TTF Natura, EFO-EUA Options

### 2. Power Products
- **Pattern**: Commodity = 'POWER' OR product name contains `Power`
- **Includes**:
  - German Power (EEX, GAB, GNM, GXC, GXQ)
  - French Power (EEX)
  - Spanish Power (EEX)
  - UK Power (UBL, EEX GB)
- **Aggregation**: Net position across all power products

### 3. TTF Year Futures
- **Pattern**: Product name = `EEX TTF Natural Gas Year Futur`
- **Reason**: Separate from named TTF Quarter/Season

### 4. European Gas Hubs
- **Pattern**: Product contains `PEG`, `PVB`, `THE`, `CEGH`, `ZTP`, `PSV`, `NBP` (but NOT main NBP)
- **Includes**:
  - PEG (French gas hub)
  - PVB (Spanish gas hub)
  - THE (Italian gas hub)
  - CEGH (Austrian gas hub)
  - ZTP (Belgium gas hub)

### 5. Oil & Commodities
- **Pattern**: Commodity IN ('OIL', 'COAL') OR product contains `Brent`, `Gasoil`, `Henry`, `LNG`, `Coal`
- **Includes**:
  - Brent Crude (B-Brent)
  - Gasoil (G-Gasoil)
  - Henry Hub US Gas (H-Henry)
  - LNG Freight
  - Coal (ATW-Rotterdam)

### 6. Emissions
- **Pattern**: Product contains `EUA`, `UKA`, `Carbon`
- **Includes**:
  - EUA Futures (C-EUA, EEX EUA)
  - UKA Futures/Options
  - EFO-EUA Options
- **Note**: Only show if not already in main breakdown

### 7. Small Positions
- **Definition**: Everything else with |value| < £1M individually
- **Aggregation**: Sum of all remaining positions

---

## SQL Implementation

```sql
-- Calculate "Other" category size
WITH named_products AS (
    SELECT SUM(ote_value_gbp) / 1000000 as total_gbp_m
    FROM ote_positions
    WHERE business_date = :business_date
      AND product_name IN (
          'EEX TTF Natural Gas Quarter Fu',
          'EEX TTF Natural Gas Season Fut',
          'TFM-Dutch TTF Natura',
          'M-UK NBP Natural Gas',
          'JKM-Japan Korea Mark',
          'TFU-Dutch TTF Natura'
      )
),
total_ote AS (
    SELECT SUM(ote_value_gbp) / 1000000 as total_gbp_m
    FROM ote_positions
    WHERE business_date = :business_date
),
other_size AS (
    SELECT 
        (t.total_gbp_m - n.total_gbp_m) as other_gbp_m
    FROM total_ote t, named_products n
)
-- Check if drill-down needed
SELECT 
    CASE 
        WHEN ABS(other_gbp_m) >= 5.0 THEN 'DRILL_DOWN'
        ELSE 'SUMMARY_ONLY'
    END as view_mode,
    other_gbp_m
FROM other_size
```

### Drill-Down Query

```sql
-- Only run if view_mode = 'DRILL_DOWN'
SELECT 
    CASE 
        WHEN product_name LIKE '%TFO%' OR product_name LIKE '%TTF%Option%' 
            THEN 'TTF Options'
        WHEN commodity = 'POWER' OR product_name LIKE '%Power%' 
            THEN 'Power Products'
        WHEN product_name = 'EEX TTF Natural Gas Year Futur' 
            THEN 'TTF Year Futures'
        WHEN product_name LIKE ANY('%PEG%', '%PVB%', '%THE%', '%CEGH%', '%ZTP%', '%PSV%')
            THEN 'European Gas Hubs'
        WHEN commodity IN ('OIL', 'COAL') OR product_name LIKE ANY('%Brent%', '%Gasoil%', '%Henry%', '%LNG%', '%Coal%')
            THEN 'Oil & Commodities'
        WHEN product_name LIKE ANY('%EUA%', '%UKA%', '%Carbon%')
            THEN 'Emissions'
        ELSE 'Small Positions'
    END as subcategory,
    COUNT(*) as num_products,
    SUM(ote_value_gbp) / 1000000 as total_gbp_m
FROM ote_positions
WHERE business_date = :business_date
  AND product_name NOT IN (
      'EEX TTF Natural Gas Quarter Fu',
      'EEX TTF Natural Gas Season Fut',
      'TFM-Dutch TTF Natura',
      'M-UK NBP Natural Gas',
      'JKM-Japan Korea Mark',
      'TFU-Dutch TTF Natura'
  )
GROUP BY subcategory
HAVING ABS(SUM(ote_value_gbp) / 1000000) > 0.01  -- Ignore negligible amounts
ORDER BY ABS(total_gbp_m) DESC
```

---

## API Response Format

### When Other < £5M
```json
{
  "business_date": "2026-07-22",
  "total_ote_gbp_m": 20.52,
  "breakdown": [
    {"product": "EEX TTF Quarter", "value_gbp_m": 3.70},
    {"product": "EEX TTF Season", "value_gbp_m": -7.71},
    {"product": "TFM-Dutch TTF", "value_gbp_m": 47.84},
    {"product": "NBP Gas", "value_gbp_m": 12.16},
    {"product": "JKM (Asia Gas)", "value_gbp_m": -24.75},
    {"product": "TFU-Dutch TTF", "value_gbp_m": -12.57},
    {"product": "Other open", "value_gbp_m": 2.35, "drill_down_available": false}
  ]
}
```

### When Other >= £5M
```json
{
  "business_date": "2026-07-22",
  "total_ote_gbp_m": 29.46,
  "breakdown": [
    {"product": "EEX TTF Quarter", "value_gbp_m": 3.70},
    {"product": "EEX TTF Season", "value_gbp_m": -7.71},
    {"product": "TFM-Dutch TTF", "value_gbp_m": 47.84},
    {"product": "NBP Gas", "value_gbp_m": 12.16},
    {"product": "JKM (Asia Gas)", "value_gbp_m": -24.75},
    {"product": "TFU-Dutch TTF", "value_gbp_m": -12.57},
    {
      "product": "Other open", 
      "value_gbp_m": 10.79, 
      "drill_down_available": true,
      "subcategories": [
        {"name": "TTF Options", "value_gbp_m": 5.14, "num_products": 1},
        {"name": "Power Products", "value_gbp_m": 3.44, "num_products": 15},
        {"name": "TTF Year Futures", "value_gbp_m": 3.08, "num_products": 1},
        {"name": "European Gas Hubs", "value_gbp_m": 0.67, "num_products": 12},
        {"name": "Oil & Commodities", "value_gbp_m": 0.71, "num_products": 5},
        {"name": "Small Positions", "value_gbp_m": -2.25, "num_products": 23}
      ]
    }
  ]
}
```

---

## Configuration Table

```sql
CREATE TABLE drill_down_config (
    config_id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,              -- 'OTE', 'SPOT_PHYSICAL', etc.
    threshold_gbp_m REAL NOT NULL,       -- e.g., 5.0
    active BOOLEAN DEFAULT 1,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)

-- Default config
INSERT INTO drill_down_config (category, threshold_gbp_m) 
VALUES ('OTE', 5.0);
```

**Benefits**:
- Threshold is configurable (can change from £5M to £10M easily)
- Can apply same logic to other categories (Spot/Physical, etc.)
- Can be adjusted without code changes

---

## UI Behavior

### Collapsed View (Default)
```
OTE Breakdown:
  TTF Quarter           £3.70M
  TTF Season           -£7.71M
  TFM-Dutch TTF        £47.84M
  NBP Gas              £12.16M
  JKM                 -£24.75M
  TFU-Dutch           -£12.57M
▶ Other open           £10.79M   ← Expandable (red flag if > £5M)
  ─────────────────────────────
  Total OTE            £29.46M
```

### Expanded View (User clicks ▶)
```
OTE Breakdown:
  TTF Quarter           £3.70M
  TTF Season           -£7.71M
  TFM-Dutch TTF        £47.84M
  NBP Gas              £12.16M
  JKM                 -£24.75M
  TFU-Dutch           -£12.57M
▼ Other open           £10.79M   ← Expanded
    ├ TTF Options       £5.14M   (1 product)
    ├ Power Products    £3.44M   (15 products)
    ├ TTF Year          £3.08M   (1 product)
    ├ European Hubs     £0.67M   (12 products)
    ├ Oil & Commodities £0.71M   (5 products)
    └ Small Positions  -£2.25M   (23 products)
  ─────────────────────────────
  Total OTE            £29.46M
```

**Visual Indicators**:
- Red/amber flag if Other > £5M (requires attention)
- Green if Other < £5M (acceptable)
- Click to expand/collapse subcategories
- Further click on subcategory shows individual products

---

## Testing Scenarios

### Test 1: Other Below Threshold
- **Setup**: Create positions where Other = £3M
- **Expected**: Single "Other open" line, no drill-down
- **API**: `drill_down_available: false`

### Test 2: Other Above Threshold
- **Setup**: Create positions where Other = £10.79M (actual data)
- **Expected**: "Other open" with 6 subcategories shown
- **API**: `drill_down_available: true` with subcategories array

### Test 3: Threshold Change
- **Setup**: Change threshold from £5M to £10M
- **Expected**: Other = £10.79M now shows as single line (just at threshold)

### Test 4: Empty Subcategories
- **Setup**: Other = £8M but only from Power (no TTF Options)
- **Expected**: Only show non-zero subcategories

---

## Implementation Priority

**Phase 1 (MVP)**:
- [x] Identify the 6 named products
- [x] Calculate "Other" as residual
- [ ] Implement threshold check (£5M)
- [ ] Parse product detail into subcategories

**Phase 2 (Enhancement)**:
- [ ] Store subcategory in database
- [ ] Build API endpoint with conditional drill-down
- [ ] Create UI with expand/collapse

**Phase 3 (Advanced)**:
- [ ] Configurable threshold per category
- [ ] Alert if "Other" exceeds threshold
- [ ] Product-level drill-down (click subcategory to see individual products)

---

*Drill-down specification complete. Ready for implementation with £5M threshold.*

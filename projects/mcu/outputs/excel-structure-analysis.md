# Excel Structure Analysis: LwgSummary Tab

**Source**: `1. CeMarginMoveSummary_20260722.xlsm`, Tab: `LwgSummary`, Range: `L48:S158`

**Analysis Date**: 2026-07-23

---

## Discovered Structure

### Column Layout (Key Columns I-S)

| Column | Header Row 80 | Header Row 81 | Purpose |
|--------|---------------|---------------|---------|
| **I** | "Today" | "Reference date" | **Product/Item Description** |
| **J** | | | **Currency** (EUR, GBP, USD) |
| **K** | "2026-07-21" | "2026-07-22" | **T (Today) Value** - Current date position |
| **L** | | "Position" | **Position Type** (BNP CEL, Long, Short, etc.) |
| **M-O** | | | (Empty - spacing) |
| **P** | "2026-07-15" | "2026-07-22" | **T-1 (Prior Date) Value** - Comparison date position |
| **Q-R** | | | **Movement Calculation** (likely DOD/WOW) |
| **S** | | | **Variance / Change Since** |

### Data Hierarchy (Rows 82-110)

The data follows a **waterfall/cascade structure** explaining total margin movement:

```
LEVEL 1: Granular Products (rows 82-101)
├── EEX TTF Natural Gas Month Futures (EUR)    : K=0.057,  P=-0.513
├── EEX TTF Natural Gas Quarter Futures (EUR)  : K=3.695,  P=9.833
├── EEX TTF Natural Gas Season Futures         : K=-7.710, P=-14.757
├── EEX TTF Natural Gas Year Futures           : K=3.083,  P=4.418
├── TFM-Dutch TTF Natural Gas (EUR)            : K=47.845, P=111.273
│   └── Subtotal: TTF Futures                  : K=46.970, P=110.255
├── TFO-Dutch TTF Natural Gas Options          : K=5.142,  P=10.355
├── M-UK NBP Natural Gas (GBP)                 : K=12.158, P=33.273
│   └── NBP (Long position)
├── JKM-Japan Korea Marker (USD)               : K=-24.751, P=-45.443
│   └── JKM (Short position)
├── TFU-Dutch TTF Natural (USD)                : K=-12.571, P=-27.611
│   └── TFU (Short position)
├── C-EUA Future (Emissions)                   : K=-1.193,  P=-2.934
├── UKA-UKA Futures (Emissions)                : K=-1.193,  P=-1.545
│   └── Subtotal: Emissions' futures (Short)   : K=-2.387,  P=-4.479
├── B-Brent Crude Future                       : K=0.595,   P=0.197
│   └── Brent Futures (Long)                   : K=0.595,   P=0.0
└── Other moves on open positions              : K=4.299,   P=12.884

LEVEL 2: Aggregated Categories (rows 102-110)
├── Total BNP Open movement                    : K=29.455,  P=89.235
├── Spot/Physical Delivery                     : K=23.509,  P=-43.822
├── Cascading of expired contracts             : K=-0.280,  P=0.056
├── Other                                      : K=-0.029,  P=0.128
├── BNP CEL Margin call (Total)                : K=52.656,  P=45.596
├── BNP CET Margin Call                        : K=0.732,   P=1.136
├── SocGen                                     : K=0.0,     P=-4.409
├── CSA                                        : K=11.723,  P=63.700
└── TSO                                        : K=0.0,     P=0.271

LEVEL 3: Analysis Sections (rows 120-158)
├── IM Nasdaq novated to BNP                   : -33.00
├── Cash from scheduled exchange payments      : -2052.48 (Daily delivery/settlement)
├── Options VM explain
├── Initial Margin Analysis (CEL/BNP)
├── SPECIAL DELIVERY                           : Row 155
└── ADDITIONAL MARGIN                          : Row 158
```

---

## Data Model Requirements

### What the User Needs

**Comparison**: Any two dates (not just consecutive days)
- Example: 2026-07-22 vs 2026-07-15 (week-over-week)
- Example: 2026-07-22 vs 2026-06-30 (month-end)

**Drill-Down Variance Analysis**:
1. **Top line**: "BNP CEL Margin call changed by £7.06M"
2. **Breakdown by category**:
   - Open positions movement: +£40M
   - Physical delivery: -£67M
   - Net: +£7.06M
3. **Drill into products**:
   - TTF Gas increased: +£63M
   - NBP Gas decreased: -£21M
   - Emissions: +£2M
4. **Reconciliation**: Sum of components = Total

### Required Database Schema

**Current schema is INSUFFICIENT**. We need these fields:

```sql
CREATE TABLE margin_positions (
    position_id INTEGER PRIMARY KEY,
    load_id INTEGER NOT NULL,
    business_date DATE NOT NULL,
    
    -- Hierarchy fields
    level INTEGER NOT NULL,              -- 1=granular product, 2=category, 3=total
    parent_category TEXT,                -- Links to parent row
    
    -- Classification
    clearer TEXT NOT NULL,               -- BNP, SocGen
    entity TEXT,                         -- CEL, CET
    margin_type TEXT NOT NULL,           -- Exchange Margin, CSA, TSO
    
    -- Product detail (for level 1)
    product TEXT,                        -- 'EEX TTF Natural Gas Month Futures'
    product_type TEXT,                   -- 'Futures', 'Options', 'Physical'
    commodity TEXT,                      -- 'Gas', 'Power', 'Emissions', 'Oil'
    exchange TEXT,                       -- 'EEX', 'ICE', 'CME'
    position_direction TEXT,             -- 'Long', 'Short', NULL
    
    -- Values
    currency TEXT DEFAULT 'GBP',         -- EUR, GBP, USD
    position_value REAL NOT NULL,
    
    -- Comparison support
    is_summary BOOLEAN DEFAULT 0,        -- TRUE for aggregated rows
    summary_of TEXT,                     -- Category this summarizes
    
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (load_id) REFERENCES data_loads(load_id)
)
```

**New indexes needed**:
```sql
CREATE INDEX idx_positions_hierarchy ON margin_positions(level, parent_category);
CREATE INDEX idx_positions_commodity ON margin_positions(commodity);
CREATE INDEX idx_positions_product ON margin_positions(product);
```

### Comparison Query Pattern

To replicate "Column K (2026-07-22) vs Column P (2026-07-15)":

```sql
SELECT 
    p.level,
    p.parent_category,
    p.product,
    p.commodity,
    p.position_direction,
    t1.position_value as value_t1,      -- 2026-07-15
    t2.position_value as value_t2,      -- 2026-07-22
    (t2.position_value - t1.position_value) as movement,
    p.currency
FROM margin_positions p
LEFT JOIN margin_positions t1 
    ON t1.product = p.product 
    AND t1.business_date = '2026-07-15'
    AND t1.clearer = p.clearer
LEFT JOIN margin_positions t2 
    ON t2.product = p.product 
    AND t2.business_date = '2026-07-22'
    AND t2.clearer = p.clearer
WHERE p.level = 1  -- Start with granular products
ORDER BY p.parent_category, p.product
```

### Reconciliation Check

```sql
-- Verify that sum of level 1 (products) = level 2 (category totals)
SELECT 
    parent_category,
    SUM(position_value) as products_total
FROM margin_positions
WHERE business_date = '2026-07-22'
  AND level = 1
  AND parent_category = 'Total BNP Open movement'
GROUP BY parent_category
-- Should equal the level=2 row for 'Total BNP Open movement'
```

---

## Example Data Rows

**Level 1 - Granular Product**:
```
business_date: 2026-07-22
level: 1
parent_category: 'Total BNP Open movement'
clearer: 'BNP'
entity: 'CEL'
margin_type: 'Exchange Margin'
product: 'EEX TTF Natural Gas Month Futures'
commodity: 'Gas'
exchange: 'EEX'
position_direction: 'Long'
currency: 'EUR'
position_value: 0.057
```

**Level 2 - Category Summary**:
```
business_date: 2026-07-22
level: 2
parent_category: 'BNP CEL Margin call'
clearer: 'BNP'
entity: 'CEL'
margin_type: 'Exchange Margin'
product: 'Total BNP Open movement'
is_summary: TRUE
summary_of: 'Open Positions'
position_value: 29.455
```

**Level 3 - Top Line**:
```
business_date: 2026-07-22
level: 3
clearer: 'BNP'
entity: 'CEL'
margin_type: 'Exchange Margin'
product: 'BNP CEL Margin call'
is_summary: TRUE
position_value: 52.656
```

---

## Recommended Changes to Schema

**MUST ADD**:
1. `level` - for hierarchy (1=product, 2=category, 3=total)
2. `parent_category` - links products to their summary
3. `product` - full product name
4. `commodity` - Gas, Power, Emissions, Oil
5. `product_type` - Futures, Options, Physical
6. `position_direction` - Long, Short (for display)
7. `is_summary` - boolean flag for aggregated rows

**OPTIONAL BUT USEFUL**:
8. `exchange` - EEX, ICE, CME
9. `contract_period` - Month, Quarter, Season, Year
10. `summary_of` - text description of what this row aggregates

---

## Next Steps

1. **Update database schema** to include hierarchy and product fields
2. **Write migration script** (or recreate from scratch since no production data yet)
3. **Update CSV parser** to extract product, commodity, hierarchy from source files
4. **Build comparison query logic** that:
   - Queries two dates
   - Calculates movements at each level
   - Validates reconciliation (sum of children = parent)
5. **Create CLI tool**: `python compare.py 2026-07-15 2026-07-22`

---

## Questions for User

1. **Do ALL source files have this hierarchical structure?** Or is this specific to the Excel summary?
2. **Are the granular products in the CSV files**, or do we need to parse the Excel workbook itself?
3. **Which files contain product-level detail?**
   - `Detailed_Open_Pos_CEL U_*.csv` → Product-level positions?
   - `PnS_CEL U_*.csv` → Product-level P&L?
   - `MC_Statement_CEL U_*.csv` → Summary only?

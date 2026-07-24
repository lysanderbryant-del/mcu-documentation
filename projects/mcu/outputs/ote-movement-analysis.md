# OTE Movement Analysis: How Excel Summarizes Key Movements

**Date**: 2026-07-23  
**Purpose**: Document how the Excel file calculates and presents OTE (Open Trade Equity) movements

---

## The Movement Structure

The Excel tracks **three types of movements**:

1. **DOD (Day over Day)**: Today vs Yesterday
2. **WOW (Week over Week)**: Today vs 7 days ago (Jul 22 vs Jul 15)
3. **Since Baseline**: Today vs a reference date (Feb 27, 2026)

---

## Source: BnppCelOtePivot Tab

**Data Flow**:
```
CELOteData (raw data from CSV)
    ↓
BnppCelOtePivot (Pivot table with date comparisons)
    ↓
CeMarginMoveDaily & LwgSummary (Movement analysis)
```

### BnppCelOtePivot Structure

| Column | Date | Purpose |
|--------|------|---------|
| D | 2026-07-15 | Week ago (T-7) |
| E | 2026-07-21 | Yesterday (T-1) |
| F | 2026-07-22 | Today (T) |
| L | - | **DOD** (Day over Day) = F - E |
| N | - | **WOW** (Week over Week) = F - D |

**Product rows include**:
- Product-level detail (TTF, NBP, JKM, etc.)
- Currency aggregations (EUR, GBP, USD)
- Summary totals

---

## Movement by Currency (Top Level)

### Week-over-Week Movement (Jul 22 vs Jul 15)

| Currency | Jul 15 | Jul 22 | WOW Movement |
|----------|---------|---------|--------------|
| EUR | £539.84M | £690.97M | **+£128.46M** ⬆️ |
| GBP | £56.94M | £90.06M | **+£33.11M** ⬆️ |
| USD | -£296.42M | -£392.87M | **-£72.34M** ⬇️ |
| **Total OTE** | **£300.36M** | **£388.16M** | **+£89.23M** |

**Key Insight**: Overall OTE increased by £89M week-over-week, driven primarily by EUR positions (+£128M) partially offset by increased USD shorts (-£72M).

---

## Movement by Product Category

### Gas Products (Major Contributor)

**TTF (Dutch Gas)**:

| Product | Jul 15 | Jul 22 | WOW Movement |
|---------|---------|---------|--------------|
| EEX TTF Month | -£0.51M | £0.06M | **+£0.57M** |
| EEX TTF Quarter | £9.83M | £3.70M | **-£6.13M** ⬇️ |
| EEX TTF Season | -£14.76M | -£7.71M | **+£7.05M** ⬆️ |
| EEX TTF Year | £4.42M | £3.08M | **-£1.34M** |
| TFM-Dutch TTF | £111.27M | £47.84M | **-£63.43M** ⬇️⬇️ |
| **TTF Total** | **£110.25M** | **£46.97M** | **-£63.28M** ⬇️ |

**Interpretation**: TTF positions DECREASED significantly (-£63M), mainly driven by TFM-Dutch TTF reduction (-£63M). This was a major unwind of long gas positions.

**NBP (UK Gas)**:

| Product | Jul 15 | Jul 22 | WOW Movement |
|---------|---------|---------|--------------|
| M-UK NBP Natural Gas | £33.27M | £12.16M | **-£21.11M** ⬇️ |

**Interpretation**: UK gas exposure also reduced significantly (-£21M).

**Other Gas**:

| Product | Jul 15 | Jul 22 | WOW Movement |
|---------|---------|---------|--------------|
| JKM (Asia Gas) | -£45.44M | -£24.75M | **+£20.69M** ⬆️ (less short) |
| TFU-Dutch TTF USD | -£27.61M | -£12.57M | **+£15.04M** ⬆️ (less short) |

---

### Options (TTF Options)

| Product | Jul 15 | Jul 22 | WOW Movement |
|---------|---------|---------|--------------|
| TFO-Dutch TTF Options | £10.36M | £5.14M | **-£5.22M** ⬇️ |

---

### Emissions

| Product | Jul 15 | Jul 22 | WOW Movement |
|---------|---------|---------|--------------|
| C-EUA Future | -£2.93M | -£1.19M | **+£1.74M** ⬆️ (less short) |
| UKA Futures | -£1.54M | -£1.19M | **+£0.35M** |
| **Emissions Total** | **-£4.48M** | **-£2.39M** | **+£2.09M** ⬆️ |

---

### Oil

| Product | Jul 15 | Jul 22 | WOW Movement |
|---------|---------|---------|--------------|
| Brent Crude | £0.00M | £0.59M | **+£0.59M** ⬆️ (new position) |

---

## Summary: Key OTE Movements

### The Story (Week-over-Week)

```
Starting OTE (Jul 15):              £300.36M

Major Decreases:
  ├─ TFM-Dutch TTF unwound          -£63.43M ⬇️⬇️ (largest movement)
  ├─ NBP Gas reduced                -£21.11M ⬇️
  ├─ TTF Quarter futures down       -£6.13M
  └─ TTF Options reduced            -£5.22M
                                    ──────────
  Total Decreases:                  -£95.89M

Major Increases:
  ├─ JKM short covered              +£20.69M ⬆️ (less short)
  ├─ TFU-TTF short covered          +£15.04M ⬆️
  ├─ TTF Season increased           +£7.05M
  ├─ Emissions shorts covered       +£2.09M
  ├─ Brent position added           +£0.59M
  └─ Other movements                +£139.66M ⬆️⬆️ (NET from currency)
                                    ──────────
  Total Increases:                  +£185.12M

Ending OTE (Jul 22):                £388.16M
                                    ══════════
Net Movement:                       +£89.23M ⬆️
```

**Key Takeaway**: Despite unwinding major TTF and NBP gas positions (-£85M), overall OTE increased by £89M due to currency revaluation effects and covering of USD short positions.

---

## How CeMarginMoveDaily Displays This

**Row 33**: Total OTE = £29.46M (GBP equivalent after FX)

**Breakdown shown**:
```
EEX TTF Natural Gas Quarter:     £3.70M
EEX TTF Natural Gas Season:     -£7.71M
TFM-Dutch TTF Natura:           £47.84M
M-UK NBP Natural Gas:           £12.16M
JKM-Japan Korea:               -£24.75M
TFU-Dutch TTF:                 -£12.57M
Other open:                     £10.79M
──────────────────────────────────────
Total OTE:                      £29.46M ✓
```

**Note**: The £29.46M is the **DOD (day-over-day) movement**, not the absolute position. The absolute position is £388.16M.

---

## Database Schema for Movement Tracking

### Table: `ote_positions`

```sql
CREATE TABLE ote_positions (
    ote_id INTEGER PRIMARY KEY,
    business_date DATE NOT NULL,
    clearer TEXT NOT NULL,
    entity TEXT NOT NULL,
    product_name TEXT NOT NULL,
    exchange TEXT,                      -- 'EEX', 'ICE', etc.
    commodity TEXT,                     -- 'Gas', 'Emissions', 'Oil'
    contract_type TEXT,                 -- 'Future', 'Option'
    position_direction TEXT,            -- 'Long', 'Short'
    original_currency TEXT NOT NULL,
    position_value_native REAL,         -- In original currency
    ote_value_native REAL NOT NULL,     -- Open Trade Equity in native currency
    ote_value_gbp REAL,                 -- OTE converted to GBP
    source_file TEXT NOT NULL,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Query for Movement Analysis

```sql
-- Week-over-Week Movement by Product
WITH current_week AS (
    SELECT 
        product_name,
        commodity,
        SUM(ote_value_gbp / 1000000) as ote_gbp_m
    FROM ote_positions
    WHERE business_date = '2026-07-22'
      AND clearer = 'BNP'
      AND entity = 'CEL'
    GROUP BY product_name, commodity
),
prior_week AS (
    SELECT 
        product_name,
        commodity,
        SUM(ote_value_gbp / 1000000) as ote_gbp_m
    FROM ote_positions
    WHERE business_date = '2026-07-15'
      AND clearer = 'BNP'
      AND entity = 'CEL'
    GROUP BY product_name, commodity
)
SELECT 
    COALESCE(c.product_name, p.product_name) as product,
    COALESCE(c.commodity, p.commodity) as commodity,
    COALESCE(p.ote_gbp_m, 0) as jul_15,
    COALESCE(c.ote_value_gbp, 0) as jul_22,
    COALESCE(c.ote_gbp_m, 0) - COALESCE(p.ote_gbp_m, 0) as wow_movement
FROM current_week c
FULL OUTER JOIN prior_week p 
    ON p.product_name = c.product_name
ORDER BY ABS(COALESCE(c.ote_gbp_m, 0) - COALESCE(p.ote_gbp_m, 0)) DESC
```

**Expected Output**:
```
Product                      | Commodity | Jul 15   | Jul 22   | WOW Movement
-----------------------------|-----------|----------|----------|-------------
TFM-Dutch TTF Natura         | Gas       | 111.27   | 47.84    | -63.43 ⬇️⬇️
M-UK NBP Natural Gas         | Gas       | 33.27    | 12.16    | -21.11 ⬇️
JKM-Japan Korea Marker       | Gas       | -45.44   | -24.75   | +20.69 ⬆️
TFU-Dutch TTF Natura         | Gas       | -27.61   | -12.57   | +15.04 ⬆️
...
```

---

## Automated Daily Movement Report

### Summary Format (Replicate Excel)

```python
def generate_ote_movement_summary(business_date, comparison_date):
    """
    Generate OTE movement summary similar to Excel.
    
    Args:
        business_date: Today (e.g., 2026-07-22)
        comparison_date: Comparison date (e.g., 2026-07-15 for WOW)
    
    Returns:
        Movement summary by product with key drivers
    """
    
    # 1. Query OTE positions for both dates
    current = query_ote_positions(business_date)
    prior = query_ote_positions(comparison_date)
    
    # 2. Calculate movements by product
    movements = calculate_movements(current, prior)
    
    # 3. Sort by absolute movement size
    movements.sort(key=lambda x: abs(x['movement']), reverse=True)
    
    # 4. Format summary
    summary = {
        'total_ote_current': sum(x['current'] for x in movements),
        'total_ote_prior': sum(x['prior'] for x in movements),
        'total_movement': sum(x['movement'] for x in movements),
        'top_increases': [m for m in movements if m['movement'] > 0][:5],
        'top_decreases': [m for m in movements if m['movement'] < 0][:5],
        'by_commodity': aggregate_by_commodity(movements),
        'detail': movements
    }
    
    return summary
```

### Output Format

```
OTE Movement Summary
Period: 2026-07-15 → 2026-07-22 (Week-over-Week)

TOTAL OTE:
  Jul 15: £300.36M
  Jul 22: £388.16M
  Movement: +£89.23M ⬆️

TOP 5 DECREASES:
  1. TFM-Dutch TTF Natura        -£63.43M ⬇️⬇️ (Gas)
  2. M-UK NBP Natural Gas        -£21.11M ⬇️   (Gas)
  3. EEX TTF Quarter             -£6.13M  ⬇️   (Gas)
  4. TFO-Dutch TTF Options       -£5.22M  ⬇️   (Gas Options)
  5. EEX TTF Year                -£1.34M       (Gas)

TOP 5 INCREASES:
  1. JKM-Japan Korea (short)     +£20.69M ⬆️   (Gas - short covered)
  2. TFU-Dutch TTF (short)       +£15.04M ⬆️   (Gas - short covered)
  3. EEX TTF Season              +£7.05M  ⬆️   (Gas)
  4. C-EUA Emissions (short)     +£1.74M       (Emissions - short covered)
  5. Brent Crude                 +£0.59M       (Oil - new position)

BY COMMODITY:
  Gas:       -£68.49M  (Major reduction in long TTF/NBP, covered shorts)
  Emissions: +£2.09M   (Covered short positions)
  Oil:       +£0.59M   (New long Brent position)
```

---

## Implementation Steps

1. **Parse Detailed_Open_Pos CSV**
   - Extract product-level OTE
   - Store in `ote_positions` table
   - Tag with source file

2. **Build Movement Calculator**
   - Compare two dates
   - Calculate by product
   - Aggregate by commodity

3. **Generate Summary Report**
   - Top movers (increases/decreases)
   - Commodity aggregation
   - Position direction (long vs short)

4. **Display in UI**
   - Interactive date picker
   - Sortable movement table
   - Drill-down by commodity
   - Charts showing movement drivers

---

*OTE movement analysis complete. Ready for implementation.*

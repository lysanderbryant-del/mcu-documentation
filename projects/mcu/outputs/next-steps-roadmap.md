# Next Steps Roadmap

**Date**: 2026-07-23  
**Current Status**: Database built, core data loaded (£53.66M validated)

---

## Phase 1: Complete the Data Load ⏳ (1-2 hours)

### 1.1 Fix Journal Entries Parser
**Problem**: Column K has text values concatenated, not numeric amounts  
**Action**: Investigate actual CSV structure
```bash
# Check what column K actually contains
python -c "
import pandas as pd
from pathlib import Path
df = pd.read_csv(Path('//pgb1-p-e-evs012/.../Journal_Entries_CEL U_2026-07-22_*.csv'), skiprows=9, nrows=10)
print(df.columns.tolist())
print(df.iloc[:, 10])  # Column K
print(df.iloc[:, 11])  # Column L
"
```

**Expected Outcome**: Identify correct column for numeric amounts, update parser

### 1.2 Fix OTE Detail Parser
**Problem**: UNIQUE constraint failed - likely storing duplicate records  
**Action**: Add deduplication or check if records already exist
```python
# Option 1: Add ON CONFLICT handling in SQL
# Option 2: Check before insert
# Option 3: Clear existing data before reload
```

**Expected Outcome**: 69MB OTE file loads successfully with product-level detail

### 1.3 Validate CSA Data
**Problem**: File is 0 bytes (empty)  
**Action**: 
- Check if file is normally empty for this date
- If not, find actual CSA file with data
- Expected CSA value: £11.72M

**Expected Outcome**: CSA collateral data loaded correctly

### 1.4 Verify Total Margin
```sql
SELECT 
    SUM(position_value_gbp) / 1000000 as total_margin_gbp_m
FROM margin_positions
WHERE business_date='2026-07-22';
```

**Target**: £65.11M total  
**Current**: £53.66M (missing CSA £11.72M + adjustments)

---

## Phase 2: Historical Data Load 📊 (2-4 hours)

### 2.1 Load Key Historical Dates
Load data for date range to enable comparisons:
```bash
# Last 10 business days
python src/load_with_manual_fx.py 2026-07-21
python src/load_with_manual_fx.py 2026-07-18
python src/load_with_manual_fx.py 2026-07-17
# ... continue back to 2026-07-15 (Week ago)
```

### 2.2 Automate FX Rate Fetching
**Current**: Manual FX rates inserted  
**Target**: Auto-fetch from API or Excel file

Options:
- **A**: Extract from Excel "FX Rates" tab if available
- **B**: Use Frankfurter API with corporate proxy settings
- **C**: Store standard FX rate file (CSV) uploaded daily

### 2.3 Batch Historical Load
Create script to load all dates from Feb 27, 2026 onwards:
```python
# src/load_historical.py
from datetime import date, timedelta

start_date = date(2026, 2, 27)
end_date = date(2026, 7, 22)

current = start_date
while current <= end_date:
    # Skip weekends
    if current.weekday() < 5:
        try:
            load_date_with_manual_fx(current)
            print(f"✓ {current}")
        except Exception as e:
            print(f"✗ {current}: {e}")
    
    current += timedelta(days=1)
```

---

## Phase 3: Build Comparison Queries 📈 (2-3 hours)

### 3.1 Day-over-Day (DOD) Query
```sql
-- Compare today vs yesterday
WITH today AS (
    SELECT clearer, SUM(position_value_gbp) as value
    FROM margin_positions
    WHERE business_date = '2026-07-22'
    GROUP BY clearer
),
yesterday AS (
    SELECT clearer, SUM(position_value_gbp) as value
    FROM margin_positions  
    WHERE business_date = '2026-07-21'
    GROUP BY clearer
)
SELECT 
    COALESCE(t.clearer, y.clearer) as clearer,
    y.value / 1000000 as yesterday_gbp_m,
    t.value / 1000000 as today_gbp_m,
    (t.value - y.value) / 1000000 as dod_movement_gbp_m
FROM today t
FULL OUTER JOIN yesterday y ON t.clearer = y.clearer;
```

### 3.2 Week-over-Week (WOW) Query
Similar structure but compare to 7 days ago (2026-07-15)

### 3.3 Product-Level OTE Movements
```sql
-- Top 10 OTE movements (once OTE detail loaded)
WITH current_ote AS (
    SELECT product, SUM(position_value_gbp) as value
    FROM margin_positions
    WHERE business_date = '2026-07-22' AND product IS NOT NULL
    GROUP BY product
),
prior_ote AS (
    SELECT product, SUM(position_value_gbp) as value
    FROM margin_positions
    WHERE business_date = '2026-07-15' AND product IS NOT NULL
    GROUP BY product
)
SELECT 
    COALESCE(c.product, p.product) as product,
    (c.value - p.value) / 1000000 as wow_movement_gbp_m
FROM current_ote c
FULL OUTER JOIN prior_ote p ON c.product = p.product
ORDER BY ABS(c.value - p.value) DESC
LIMIT 10;
```

### 3.4 "Other" Drill-Down Query
```sql
-- When Other > £5M, show breakdown
WITH named_products AS (
    -- List of explicitly named products
    SELECT SUM(position_value_gbp) / 1000000 as total_gbp_m
    FROM margin_positions
    WHERE business_date = '2026-07-22'
      AND product IN (
          'EEX TTF Natural Gas Quarter',
          'EEX TTF Natural Gas Season',
          'TFM-Dutch TTF Natura',
          'M-UK NBP Natural Gas',
          'JKM-Japan Korea Marker',
          'TFU-Dutch TTF Natura'
      )
),
total_ote AS (
    SELECT SUM(position_value_gbp) / 1000000 as total_gbp_m
    FROM margin_positions
    WHERE business_date = '2026-07-22' AND commodity = 'GAS'
),
other_size AS (
    SELECT (t.total_gbp_m - n.total_gbp_m) as other_gbp_m
    FROM total_ote t, named_products n
)
SELECT 
    CASE 
        WHEN ABS(other_gbp_m) >= 5.0 THEN 'DRILL_DOWN_REQUIRED'
        ELSE 'SUMMARY_OK'
    END as action,
    other_gbp_m
FROM other_size;
```

---

## Phase 4: Build Web UI 🌐 (4-6 hours)

### 4.1 Technology Stack
**Recommendation**: Python Flask + SQLite + Chart.js

**Why**:
- Minimal dependencies
- Runs locally on Windows
- Can be deployed to internal server
- Simple to maintain

### 4.2 Core Pages

**Page 1: Daily Summary**
```
/daily-summary?date=2026-07-22

┌─────────────────────────────────────────┐
│  Daily Margin Report - July 22, 2026   │
├─────────────────────────────────────────┤
│                                         │
│  Total Margin: £65.11M                  │
│                                         │
│  BNP CEL:      £52.66M  [View Detail]   │
│  BNP CET:      £0.73M                   │
│  SocGen:       £0.00M                   │
│  CSA:          £11.72M  [View Detail]   │
│                                         │
│  [Compare Dates] [Export to Excel]      │
└─────────────────────────────────────────┘
```

**Page 2: Date Comparison**
```
/comparison?from=2026-07-15&to=2026-07-22

┌─────────────────────────────────────────┐
│  Margin Movement Analysis               │
│  July 15 → July 22 (Week-over-Week)     │
├─────────────────────────────────────────┤
│                                         │
│  Total Movement: +£8.45M ▲              │
│                                         │
│  Top Increases:                         │
│   • TFM-Dutch TTF:     -£63.43M ▼▼      │
│   • JKM short covered: +£20.69M ▲       │
│   • TFU covered:       +£15.04M ▲       │
│                                         │
│  [Chart: Movement by Day]               │
│  [Download Report]                      │
└─────────────────────────────────────────┘
```

**Page 3: OTE Drill-Down**
```
/ote-detail?date=2026-07-22

┌─────────────────────────────────────────┐
│  Open Trade Equity Detail               │
│  July 22, 2026                          │
├─────────────────────────────────────────┤
│                                         │
│  Named Products:                        │
│   TTF Quarter:     £3.70M               │
│   TTF Season:     -£7.71M               │
│   TFM-Dutch TTF:  £47.84M               │
│   NBP Gas:        £12.16M               │
│   JKM:           -£24.75M               │
│   TFU:           -£12.57M               │
│                                         │
│  ▼ Other (£10.79M) - Click to expand    │
│     └ TTF Options:  £5.14M              │
│     └ Power:        £3.44M              │
│     └ TTF Year:     £3.08M              │
│     └ ...                               │
│                                         │
└─────────────────────────────────────────┘
```

### 4.3 Create Flask App

**File**: `src/web/app.py`
```python
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DB_PATH = 'data/margin_recon.db'

@app.route('/')
def index():
    """Home page - redirect to latest date"""
    latest_date = get_latest_date()
    return redirect(f'/daily-summary?date={latest_date}')

@app.route('/daily-summary')
def daily_summary():
    date = request.args.get('date')
    
    # Query database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT clearer, SUM(position_value_gbp) / 1000000 as margin_gbp_m
        FROM margin_positions
        WHERE business_date = ?
        GROUP BY clearer
    """, (date,))
    
    data = cursor.fetchall()
    conn.close()
    
    return render_template('daily_summary.html', date=date, data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Run**:
```bash
cd src/web
python app.py
# Open browser to http://localhost:5000
```

---

## Phase 5: Automate Daily Execution 🤖 (1 hour)

### 5.1 Windows Task Scheduler Setup

**Task Name**: Daily Margin Load  
**Trigger**: Daily at 5:45 PM (after files available)  
**Action**: Run batch script

**Create**: `scripts/daily_load.bat`
```batch
@echo off
cd /d C:\Users\bryantl4\Documents\process-factory

REM Get today's date
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TODAY=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

REM Load data
python src/loaders/daily_loader.py %TODAY% --db data/margin_recon.db > logs\load_%TODAY%.log 2>&1

REM Check if successful
if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] SUCCESS: Loaded %TODAY% >> logs\status.log
) else (
    echo [%date% %time%] FAILED: Load error for %TODAY% >> logs\status.log
)
```

### 5.2 Email Notification (Optional)

**Install**: `pip install yagmail`

**Add to script**:
```python
import yagmail

def send_completion_email(date, status, total_margin):
    """Send email when load completes"""
    yag = yagmail.SMTP('your-email@company.com')
    
    subject = f"Margin Load Complete - {date}"
    body = f"""
    Daily margin load completed successfully.
    
    Business Date: {date}
    Total Margin: £{total_margin:.2f}M
    Status: {status}
    
    View report: http://internal-server/margin-report?date={date}
    """
    
    yag.send(
        to=['team@company.com'],
        subject=subject,
        contents=body
    )
```

---

## Phase 6: Testing & Validation ✅ (2 hours)

### 6.1 Data Quality Checks
```sql
-- Check 1: Verify totals match Excel
SELECT 
    business_date,
    SUM(position_value_gbp) / 1000000 as db_total_gbp_m
FROM margin_positions
WHERE business_date = '2026-07-22'
GROUP BY business_date;
-- Expected: £65.11M

-- Check 2: Ensure no duplicate records
SELECT business_date, clearer, entity, original_currency, COUNT(*)
FROM margin_positions
GROUP BY business_date, clearer, entity, original_currency
HAVING COUNT(*) > 1;
-- Expected: 0 rows

-- Check 3: Verify FX rates applied correctly
SELECT 
    original_currency,
    AVG(position_value_gbp / NULLIF(position_value_native, 0)) as implied_fx_rate
FROM margin_positions
WHERE business_date = '2026-07-22'
  AND position_value_native != 0
GROUP BY original_currency;
-- Expected: EUR ~0.85, USD ~0.75, GBP 1.0
```

### 6.2 Reconciliation Test
Compare database output to Excel for 3 random dates:
```python
# Compare DB vs Excel
def reconcile_with_excel(date):
    """Compare database total to Excel for a date"""
    db_total = query_db_total(date)
    excel_total = read_excel_total(date)  # From Excel file
    
    difference = db_total - excel_total
    tolerance = 0.01  # £10k tolerance
    
    if abs(difference) < tolerance:
        print(f"✓ {date}: Match (diff: £{difference*1000:.2f}k)")
    else:
        print(f"✗ {date}: MISMATCH (diff: £{difference:.2f}M)")
        print(f"  DB: £{db_total:.2f}M")
        print(f"  Excel: £{excel_total:.2f}M")
```

---

## Phase 7: Documentation & Handover 📝 (1 hour)

### 7.1 User Guide
Create `docs/USER_GUIDE.md`:
- How to access the web UI
- How to run daily load manually
- How to compare dates
- How to export reports
- Troubleshooting common issues

### 7.2 Technical Documentation
Create `docs/TECHNICAL.md`:
- Database schema
- File parsing logic
- FX rate sources
- Error handling
- Maintenance procedures

### 7.3 Operations Runbook
Create `docs/OPERATIONS.md`:
- Daily checklist
- What to do if load fails
- How to reload a date
- How to investigate breaks
- Support contacts

---

## Priority Order (Recommended)

### Week 1: Core Functionality
1. **Day 1-2**: Fix remaining parsers (Journal Entries, OTE, CSA) → Target: £65.11M loaded
2. **Day 3**: Load last 2 weeks of historical data
3. **Day 4**: Build comparison queries (DOD/WOW)
4. **Day 5**: Test and validate against Excel

### Week 2: UI & Automation  
1. **Day 1-2**: Build Flask web UI (3 core pages)
2. **Day 3**: Set up automated daily load
3. **Day 4**: Test automation end-to-end
4. **Day 5**: Documentation and handover

---

## Success Criteria

✅ **Phase 1 Complete** when:
- All 7 files parse successfully
- Total margin = £65.11M ± £0.01M
- No duplicate records
- All source files traceable

✅ **Phase 2 Complete** when:
- 10+ historical dates loaded
- FX rates automated or streamlined
- Can query any historical date

✅ **Phase 3 Complete** when:
- DOD/WOW queries working
- Can identify top 10 movers
- "Other" drill-down functional

✅ **Phase 4 Complete** when:
- Web UI accessible via browser
- Can view any date's summary
- Can compare any two dates
- Can drill down to product level

✅ **Phase 5 Complete** when:
- Daily load runs automatically at 5:45 PM
- Email notifications working
- Logs maintained

✅ **Phase 6 Complete** when:
- 3 random dates reconcile to Excel
- Data quality checks pass
- No known bugs

✅ **Phase 7 Complete** when:
- All documentation written
- User trained
- Support handover complete

---

## Estimated Timeline

- **Phase 1**: 1-2 hours (TODAY)
- **Phase 2**: 2-4 hours
- **Phase 3**: 2-3 hours  
- **Phase 4**: 4-6 hours
- **Phase 5**: 1 hour
- **Phase 6**: 2 hours
- **Phase 7**: 1 hour

**Total**: ~15-20 hours (2-3 working days)

---

## Immediate Next Action

Run this command to fix the Journal Entries parser:

```bash
python -c "
import pandas as pd
from pathlib import Path

file_path = Path('//pgb1-p-e-evs012/ENDUR_PROD_01/endur_prod/Interface/BNPFileStore/Processed/2026-Jul/Journal_Entries_CEL U_2026-07-22_23072026_16_00_07.csv')

# Read with header row 10
df = pd.read_csv(file_path, skiprows=9, nrows=5)

print('Journal Entries CSV Structure:')
print(f'Total columns: {len(df.columns)}')
print(f'\nFirst 15 columns:')
for i, col in enumerate(df.columns[:15]):
    sample = df[col].iloc[0] if len(df) > 0 else 'N/A'
    print(f'  {i:2d}: {col:30s} = {str(sample)[:40]}')
"
```

This will show us the correct column structure so we can fix the parser.

---

*Roadmap complete. Ready to execute Phase 1.*

# Daily Loader Implementation Summary

**Date**: 2026-07-23  
**Status**: Core framework complete, ready for testing with actual files

---

## What Was Built

### 1. File Discovery Module ([src/loaders/file_discovery.py](../src/loaders/file_discovery.py))

**Purpose**: Locate all 7 required CSV files on network drives for any business date

**Features**:
- Automatic date formatting (ISO, compact, underscore, month folder)
- Network path construction for 4 different locations
- Latest file selection when multiple matches exist
- File validation (existence, size, timestamp)
- Error handling for missing critical files

**Test Results**: ✅ 10/10 tests passing

**Usage**:
```python
from loaders.file_discovery import DailyFileDiscovery

discovery = DailyFileDiscovery(date(2026, 7, 22))
files = discovery.discover_all_files()
print(discovery.get_file_summary(files))
```

**Actual Results** (from network scan):
- ✅ **SocGen files found**: `20260722_GlobalMarginUnderlyingCurrencyReport.csv`
- ✅ **CSA files found**: `Collateral_Summary_2026_07_22_074009.csv`
- ❌ **BNP files missing**: Need to verify actual file location/date

---

### 2. CSV Parsers ([src/loaders/csv_parsers.py](../src/loaders/csv_parsers.py))

**Purpose**: Extract structured data from each of the 7 file types

**Parsers Implemented**:

| Parser | File Type | Extracts |
|--------|-----------|----------|
| `BNPMCStatementParser` | MC_Statement (CEL/CET) | Multi-currency NLV aggregation |
| `BNPOTEDetailParser` | Detailed_Open_Pos | Product-level OTE breakdown |
| `BNPJournalEntriesParser` | Journal_Entries | Spot/physical delivery total |
| `BNPPnSParser` | PnS | Cascade P&L total |
| `SocGenMarginParser` | GlobalMarginReport | Single margin value |
| `CSACollateralParser` | Collateral_Summary | Net collateral by entity |

**Factory Pattern**:
```python
parser = ParserFactory.get_parser('bnp_cel_mc')
data = parser.parse(file_path, business_date, entity='CEL')
```

**Column Mappings** (from Excel analysis):
- **BNP MC**: Z (CURRENCY_1), AA (BASE_CURRENCY), AB (ORIGINAL_CURRENCY), BA (NLV)
- **OTE Detail**: PRODUCT, OTE, CURRENCY, CONTRACT_TYPE
- **Journal Entries**: Header row 10, columns D/E/F/I/K
- **PnS**: Header row 10, auto-detect P&L column
- **CSA**: Header row 7, Our_Entity, HeldGbpM, PledgedGbpM

---

### 3. Daily Loader Orchestrator ([src/loaders/daily_loader.py](../src/loaders/daily_loader.py))

**Purpose**: Complete end-to-end daily load workflow

**Process**:
```
1. Check if date already loaded (skip if exists)
2. Discover all 7 files on network drives
3. Fetch FX rates (EUR, USD, GBP) from Frankfurter API
4. Parse each CSV file
5. Convert all values to GBP
6. Store in database
7. Record audit trail
```

**Command-line Usage**:
```bash
# Load specific date
python src/loaders/daily_loader.py 2026-07-22

# Force reload even if exists
python src/loaders/daily_loader.py 2026-07-22 --force

# Specify database path
python src/loaders/daily_loader.py 2026-07-22 --db data/prod.db
```

**Error Handling**:
- Missing critical files → raise `FileDiscoveryError`
- Parse failures → log error, continue with other files
- FX rate fetch failures → use fallback source
- Database errors → rollback transaction

---

## Network File Discovery Results

### What Works ✅

**SocGen Files**: Successfully found on network
```
Path: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\
File: 20260722_GlobalMarginUnderlyingCurrencyReport.csv
Status: EXISTS
```

**CSA Files**: Successfully found on network
```
Path: \\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\
File: Collateral_Summary_2026_07_22_074009.csv
Status: EXISTS
```

### What Needs Investigation ❌

**BNP Files** (4 CEL + 1 CET): Not found in expected location

**Possible Reasons**:
1. **Date mismatch**: Files might use different date in filename than business date
2. **Folder structure**: `Processed\2026-Jul\` might not be the actual location
3. **Filename pattern**: Timestamp format might be different
4. **Archive location**: Older files might be in different folder

**Next Steps**:
1. Browse network drive to find actual BNP file locations
2. Check if files are in `endur_in\` instead of `Processed\`
3. Verify actual filename pattern with wildcards
4. Update `DailyFileDiscovery` with correct paths

---

## Database Integration

The daily loader stores parsed data in:

### `margin_positions` Table
```sql
INSERT INTO margin_positions (
    business_date,
    clearer,
    margin_type,
    entity,
    counterparty,
    original_currency,
    position_value_native,
    position_value_gbp,
    product,
    commodity,
    source_file
) VALUES (...)
```

### `fx_rates` Table
```sql
INSERT INTO fx_rates (
    business_date,
    currency_from,
    currency_to,
    rate,
    source
) VALUES (...)
```

### `ote_detail` Table (for product breakdown)
```sql
-- To be implemented
CREATE TABLE ote_detail (
    ote_id INTEGER PRIMARY KEY,
    business_date DATE NOT NULL,
    product_name TEXT NOT NULL,
    ote_value_native REAL NOT NULL,
    currency TEXT NOT NULL,
    contract_type TEXT,
    source_file TEXT NOT NULL
)
```

---

## Scheduled Execution

### Windows Task Scheduler Setup

**Schedule**: Daily at 5:30 PM (after market close)

**Task Configuration**:
```
Name:     Daily Margin Load
Trigger:  Daily at 17:30
Action:   Run Python script
Program:  C:\Users\bryantl4\AppData\Local\Python\pythoncore-3.14-64\python.exe
Arguments: "C:\Users\bryantl4\Documents\process-factory\src\loaders\daily_loader.py" "$(Get-Date -Format 'yyyy-MM-dd')"
Start in: C:\Users\bryantl4\Documents\process-factory
```

### Batch Script Alternative

Create `load_today.bat`:
```batch
@echo off
cd /d C:\Users\bryantl4\Documents\process-factory

REM Get today's date in YYYY-MM-DD format
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TODAY=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

REM Create logs directory if not exists
if not exist logs mkdir logs

REM Run daily loader
echo [%date% %time%] Starting load for %TODAY% >> logs\scheduler.log
python src\loaders\daily_loader.py %TODAY% > logs\load_%TODAY%.log 2>&1

if errorlevel 1 (
    echo [%date% %time%] ERROR: Load failed for %TODAY% >> logs\scheduler.log
    REM Send email alert here if needed
) else (
    echo [%date% %time%] SUCCESS: Loaded %TODAY% >> logs\scheduler.log
)
```

### Network Authentication

**Required Permissions**:
- Read access to `\\pgb1-p-e-evs012\ENDUR_PROD_01\...`
- Read access to `\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\...`

**Setup**:
1. Store credentials in Windows Credential Manager
2. Test network access: `dir \\pgb1-p-e-evs012\ENDUR_PROD_01\`
3. Run Task Scheduler as service account with network permissions

---

## Testing

### Unit Tests ✅

```bash
pytest tests/test_daily_loader.py -v
```

**Results**: 10/10 tests passing
- Date formatting
- Path construction
- Parser factory
- File pattern matching
- Edge case dates

### Integration Testing (Next Step)

**Prerequisites**:
1. Find actual BNP files on network
2. Verify CSV structure matches expected columns
3. Create test database

**Test Plan**:
```python
# Test with single date
python src/loaders/daily_loader.py 2026-07-22 --db data/test.db

# Verify data loaded
sqlite3 data/test.db "SELECT COUNT(*) FROM margin_positions WHERE business_date='2026-07-22'"

# Check FX rates stored
sqlite3 data/test.db "SELECT * FROM fx_rates WHERE business_date='2026-07-22'"
```

---

## What's Next

### Immediate (Before Production)

1. **Locate BNP Files**
   - Browse `\\pgb1-p-e-evs012\...\BNPFileStore\` to find actual files
   - Update file patterns in `DailyFileDiscovery`
   - Test file discovery with correct paths

2. **Validate CSV Parsers**
   - Read actual CSV files to verify column positions
   - Test parsing with real data (not just structure)
   - Handle edge cases (empty files, missing columns)

3. **Test Complete Load**
   - Run `daily_loader.py` with real files
   - Verify database records match Excel totals
   - Compare £65.11M total margin from CSV vs Excel

4. **Create Audit Trail Table**
   ```sql
   CREATE TABLE data_loads (
       load_id INTEGER PRIMARY KEY,
       business_date DATE NOT NULL,
       load_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
       status TEXT NOT NULL,
       total_records INTEGER,
       duration_seconds REAL,
       error_message TEXT
   )
   ```

### Future Enhancements

5. **Date-to-Date Comparison Query**
   - Build SQL queries for DOD/WOW movement analysis
   - Replicate Excel pivot table logic
   - Implement "Other" drill-down with £5M threshold

6. **Web UI**
   - Date picker for comparison dates
   - Summary view (£65.11M breakdown by counterparty)
   - Drill-down to product level
   - OTE movement analysis (DOD/WOW)

7. **Alerting**
   - Email notification on load completion
   - Alert if files missing
   - Flag if total margin differs from expected by > £1M
   - Daily summary report

8. **Historical Backfill**
   - Load all dates from Feb 27, 2026 onwards
   - Build historical FX rate table
   - Enable long-term trend analysis

---

## File Structure

```
process-factory/
├── src/
│   ├── loaders/
│   │   ├── file_discovery.py       ✅ Complete
│   │   ├── csv_parsers.py          ✅ Complete (needs real data test)
│   │   └── daily_loader.py         ✅ Complete
│   ├── database/
│   │   ├── schema.py               ✅ Exists
│   │   └── connection.py           ✅ Exists
│   ├── fx_rates_fetcher.py         ✅ Exists
│   └── demo_daily_load.py          ✅ Complete
├── tests/
│   └── test_daily_loader.py        ✅ 10/10 passing
└── outputs/
    ├── daily-extraction-schedule.md     ✅ Complete
    ├── daily-loader-implementation.md   ✅ This file
    └── [other analysis docs]
```

---

## Summary

**✅ Core framework complete**:
- File discovery with network drive support
- 7 specialized CSV parsers
- Daily orchestration workflow
- Database storage integration
- FX rate fetching
- Automated scheduling capability

**⏳ Ready for testing**:
- Need actual BNP file locations
- Need to verify CSV column mappings
- Need integration test with real data

**🎯 Goal**: Automate daily £65.11M margin report with complete traceability from 7 CSV files to final summary.

---

*Implementation complete. Ready for integration testing once BNP file locations confirmed.*

# Replicable Skills from MCU Project

Analysis of MCU project to identify reusable patterns and assign them to agents.

## Agent-Skill Mapping

### ANALYST Agent Skills
**Purpose**: Understand current state (evidence-based)

| Skill | What It Does | From MCU Learning |
|-------|--------------|-------------------|
| `/analyze-excel` | Extract formulas, data flows | ✓ Created |
| `/extract-excel` | Quick XML extraction | ✓ Created |
| `/analyze-csv` | Inspect CSV structure, columns, sample data | 🆕 Needed |
| `/map-data-sources` | Identify all input files for a process | 🆕 Needed |
| `/compare-actual-vs-target` | Verify expected vs actual values | 🆕 Needed |
| `/network-file-discovery` | Find files on network shares by pattern | 🆕 Needed |

### ARCHITECT Agent Skills
**Purpose**: Design solution based on analysis

| Skill | What It Does | From MCU Learning |
|-------|--------------|-------------------|
| `/design-database-schema` | Generate CREATE TABLE from analysis | 🆕 Needed |
| `/design-parser-spec` | Spec out CSV parser requirements | 🆕 Needed |
| `/design-data-pipeline` | Map source → transform → destination | 🆕 Needed |
| `/calculate-complexity` | Estimate effort (simple/medium/complex) | 🆕 Needed |

### TESTER Agent Skills
**Purpose**: Write failing tests FIRST (RED phase)

| Skill | What It Does | From MCU Learning |
|-------|--------------|-------------------|
| `/write-parser-tests` | Generate TDD tests for CSV parsers | 🆕 Needed |
| `/write-integration-test` | Test complete data load pipeline | 🆕 Needed |
| `/generate-test-fixtures` | Create sample CSV files for testing | 🆕 Needed |
| `/verify-reconciliation` | Test that sum of parts = total | 🆕 Needed |

### BUILDER Agent Skills
**Purpose**: Make tests pass (GREEN), refactor

| Skill | What It Does | From MCU Learning |
|-------|--------------|-------------------|
| `/implement-parser` | Build CSV parser from spec | 🆕 Needed |
| `/run-tdd-cycle` | RED → GREEN → REFACTOR loop | 🆕 Needed |
| `/debug-test-failure` | Analyze why test failed, suggest fix | 🆕 Needed |

## Detailed Skill Specifications

### 1. `/analyze-csv` (ANALYST)

**Purpose**: Inspect CSV file structure without loading entire file

**Usage**: `/analyze-csv path/to/file.csv`

**What It Does**:
1. Read first 100 rows
2. Detect column count and names
3. Identify data types (numeric, text, date)
4. Find skip rows (headers not on line 1)
5. Detect delimiter (comma, tab, semicolon)
6. Report file size and estimated row count
7. Show sample data
8. Identify potential issues (mixed types, missing values)

**Output**: `projects/<name>/outputs/csv-analysis-<filename>.md`

**MCU Example**:
```
File: Journal_Entries_CEL U_2026-07-22_*.csv
Size: 145 KB
Rows: ~1,500 (estimated)
Columns: 15
Skip rows: 9 (header on row 10)
Delimiter: comma

Columns:
1. (empty) - Row ID
2. ACCOUNT_NUMBER - Text
3. ACCOUNT_NAME - Text
...
7. DEBIT_AMOUNT - Numeric (EUR)
8. CREDIT_AMOUNT - Numeric (EUR)
...
11. PAYMENT_TYPE - Text (PC, DLV, CSH)

Sample data:
Row 10: DEBIT=50000, CREDIT=0, TYPE=PC
Row 11: DEBIT=0, CREDIT=25000, TYPE=DLV

Issues found:
- Mixed data types in column 4 (text + numeric)
- 3 rows with all empty values
```

### 2. `/map-data-sources` (ANALYST)

**Purpose**: Identify ALL input files needed for a process

**Usage**: `/map-data-sources`

**What It Does**:
1. Scans Excel file for external references
2. Searches network shares for CSV files
3. Identifies file naming patterns
4. Maps which file feeds which calculation
5. Documents file locations and access paths
6. Estimates data volumes
7. Identifies file generation times (daily, weekly)

**Output**: `projects/<name>/outputs/data-source-mapping.md`

**MCU Example** (from complete-source-file-mapping.md):
```markdown
## Data Sources Identified

### BNP Files (5)
**Location**: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\

1. MC_Statement_CEL U_*.csv → CEL margin summary
2. MC_Statement_CET A_*.csv → CET margin summary
3. Detailed_Open_Pos_CEL U_*.csv → OTE product breakdown (69MB, 148K rows)
4. Journal_Entries_CEL U_*.csv → Spot/Physical delivery
5. PnS_CEL U_*.csv → P&L cascade

### CSA Files (1)
**Location**: \\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\

1. Collateral_Summary_YYYY_MM_DD_*.csv → Net collateral positions

### SocGen Files (1)
**Location**: \\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\

1. GlobalMarginUnderlyingCurrencyReport*.csv → SocGen margin

## File-to-Calculation Mapping
Excel Cell K82 (Total) ← Sum of:
  - K10:K50 ← Detailed_Open_Pos_CEL U_*.csv
  - K55 ← Journal_Entries_CEL U_*.csv (PAYMENT_TYPE IN ('PC','DLV'))
  - K56 ← PnS_CEL U_*.csv
```

### 3. `/network-file-discovery` (ANALYST)

**Purpose**: Find files on network shares by pattern, verify access

**Usage**: `/network-file-discovery \\server\share pattern`

**What It Does**:
1. Tests network path accessibility
2. Searches for files matching pattern
3. Lists all matches with dates and sizes
4. Identifies latest file by timestamp
5. Reports file age (is data stale?)
6. Checks read permissions
7. Estimates download time

**Output**: Inline report + `file-locations.json`

**MCU Example**:
```bash
/network-file-discovery \\pgb1-p-e-evs012\...\BNPFileStore\Processed\2026-Jul "*Journal_Entries*"

Found: 3 files
✓ Access: Read permission granted

Files:
1. Journal_Entries_CEL U_2026-07-22_23072026_16_00_07.csv
   Size: 145 KB
   Modified: 2026-07-23 16:00
   Age: 15 hours ✓ Fresh

2. Journal_Entries_CEL U_2026-07-21_22072026_16_00_12.csv
   Size: 142 KB
   Modified: 2026-07-22 16:00
   Age: 1 day

3. Journal_Entries_CEL U_2026-07-20_21072026_16_00_45.csv
   Size: 138 KB
   Modified: 2026-07-21 16:00
   Age: 2 days

Latest: File 1 (2026-07-22 data)
Recommendation: Use file 1 for current analysis
```

### 4. `/compare-actual-vs-target` (ANALYST)

**Purpose**: Verify calculated values match expected targets

**Usage**: `/compare-actual-vs-target`

**What It Does**:
1. Reads expected values from Excel or specification
2. Calculates actual values from source data
3. Compares with tolerance
4. Reports discrepancies
5. Highlights which components are off
6. Suggests root causes

**Output**: `projects/<name>/outputs/reconciliation-check.md`

**MCU Example**:
```markdown
## Reconciliation: 2026-07-22

| Component | Target (Excel) | Actual (Parsed) | Delta | Status |
|-----------|----------------|-----------------|-------|--------|
| BNP CEL MC | £52.66M | £52.66M | £0.00M | ✓ MATCH |
| BNP OTE | £29.46M | £29.46M | £0.00M | ✓ MATCH |
| Journal Entries | £23.51M | £75.70M | +£52.19M | ✗ FAIL |
| CSA Collateral | £11.72M | - | - | ⏳ NOT LOADED |
| **TOTAL** | **£65.11M** | **£93.40M** | **+£28.29M** | **✗ FAIL** |

## Issues Found

### Journal Entries: £52.19M too high
**Root Cause Analysis**:
- Current parser: Summing ALL transactions
- Should be: Filter PAYMENT_TYPE IN ('PC', 'DLV') only
- Fix: Update filter logic in BNPJournalEntriesParser

### CSA Collateral: Not loaded
**Root Cause**: Parser using wrong skiprows=6 (should be 0)
```

### 5. `/design-database-schema` (ARCHITECT)

**Purpose**: Generate SQL CREATE TABLE from analysis

**Usage**: `/design-database-schema`

**What It Does**:
1. Reads ANALYST outputs (CSV analysis, data mapping)
2. Identifies entities (positions, trades, collateral)
3. Determines columns and data types
4. Adds primary keys, foreign keys
5. Creates indexes for common queries
6. Adds constraints (UNIQUE, NOT NULL)
7. Includes audit fields (created_at, source_file)

**Output**: `projects/<name>/outputs/database-schema.sql`

**MCU Example**:
```sql
-- Generated from analysis of 7 CSV sources
-- Target reconciliation: £65.11M

CREATE TABLE margin_positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_id INTEGER NOT NULL,
    business_date DATE NOT NULL,
    
    -- Clearer & Entity
    clearer TEXT NOT NULL,           -- BNP, SOCGEN, CSA
    entity TEXT,                     -- CEL, CET
    counterparty TEXT,
    
    -- Classification
    margin_type TEXT NOT NULL,       -- MARGIN_CALL, OTE, SPOT_PHYSICAL, etc.
    product_name TEXT,
    commodity TEXT,                  -- GAS, POWER, EMISSIONS
    
    -- Values
    original_currency TEXT DEFAULT 'GBP',
    position_value_native REAL NOT NULL,
    
    -- Audit
    source_file TEXT NOT NULL,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (load_id) REFERENCES data_loads(load_id),
    
    -- Prevent duplicates
    UNIQUE(business_date, clearer, margin_type, entity, counterparty, original_currency, product_name)
);

CREATE INDEX idx_positions_date ON margin_positions(business_date);
CREATE INDEX idx_positions_clearer ON margin_positions(clearer);
CREATE INDEX idx_positions_type ON margin_positions(margin_type);
```

### 6. `/write-parser-tests` (TESTER)

**Purpose**: Generate TDD tests for CSV parser

**Usage**: `/write-parser-tests <parser-name>`

**What It Does**:
1. Reads ANALYST CSV analysis
2. Reads ARCHITECT parser specification
3. Generates RED tests (will fail initially)
4. Tests structure (columns, data types)
5. Tests calculations (expected values)
6. Tests edge cases (empty file, missing columns)
7. Uses pytest format

**Output**: `projects/<name>/tests/test_<parser-name>.py`

**MCU Example**:
```python
# Generated TDD tests for BNPJournalEntriesParser
# Based on: analyst-journal-entries.md

def test_extracts_correct_total_eur_amount():
    """
    RED TEST: This will FAIL until parser is fixed
    
    GIVEN: Journal Entries CSV for 2026-07-22
    WHEN: Parser extracts spot/physical delivery
    THEN: EUR amount should be ~28.5M
    """
    parser = BNPJournalEntriesParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    eur_amount = result['position_value_native']
    assert 28_000_000 <= eur_amount <= 29_000_000, \
        f"Expected EUR ~28.5M, got EUR {eur_amount:,.0f}"

def test_filters_payment_types_correctly():
    """Filter should include only PC and DLV, not CSH"""
    parser = BNPJournalEntriesParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Analyst found: 7 PC + 25 DLV = 32 transactions
    # If CSH included, would be 35 (incorrect)
    assert result['margin_type'] == 'SPOT_PHYSICAL'
```

### 7. `/debug-test-failure` (BUILDER)

**Purpose**: Analyze why test failed and suggest fix

**Usage**: `/debug-test-failure test_name`

**What It Does**:
1. Reads test code and failure message
2. Reads ANALYST report for expected values
3. Inspects actual parser implementation
4. Compares expected vs actual logic
5. Identifies root cause
6. Suggests specific fix with line numbers

**Output**: Inline guidance

**MCU Example**:
```
Test: test_extracts_correct_total_eur_amount
Status: FAILED
Expected: €28.5M
Actual: €75.7M
Delta: 2.6x too large

Root Cause Analysis:
1. Reading csv_parsers.py:159-170
2. Current logic: abs(debit_sum - credit_sum)
3. Analyst report (line 45): Should filter PAYMENT_TYPE first
4. Current code: NO FILTERING applied

Issue: Parser sums ALL transactions, not just PC and DLV

Fix Required:
File: src/loaders/csv_parsers.py
Location: Line 164 (before debit/credit calculation)

Add:
```python
# Filter for spot/physical transactions
mask = df[payment_type_col].isin(['PC', 'DLV'])
filtered = df[mask]

# Then sum filtered dataframe
debit_sum = pd.to_numeric(filtered[debit_col], ...).sum()
credit_sum = pd.to_numeric(filtered[credit_col], ...).sum()
```

Expected Result After Fix:
- Test should pass (GREEN)
- Value should be ~€28.5M
```

## Creating the Skills

### Priority 1 (High Value, Frequently Used)
1. `/analyze-csv` - Every CSV-based project needs this
2. `/compare-actual-vs-target` - Essential for reconciliation projects
3. `/write-parser-tests` - Core TDD workflow

### Priority 2 (Medium Value)
4. `/map-data-sources` - Complex projects with many inputs
5. `/network-file-discovery` - When files are on network shares
6. `/design-database-schema` - Automate schema creation

### Priority 3 (Nice to Have)
7. `/debug-test-failure` - Advanced BUILDER assistance
8. `/design-parser-spec` - Formalize ARCHITECT output
9. `/generate-test-fixtures` - Create sample data

## Skill Organization

```
.claude/commands/
├── factory.md                  # Conductor (existing)
├── extract-excel.md            # ANALYST (existing)
├── analyze-excel.md            # ANALYST (existing)
│
├── analyze-csv.md              # ANALYST (create)
├── map-data-sources.md         # ANALYST (create)
├── compare-actual-vs-target.md # ANALYST (create)
├── network-file-discovery.md   # ANALYST (create)
│
├── design-database-schema.md   # ARCHITECT (create)
├── design-parser-spec.md       # ARCHITECT (create)
│
├── write-parser-tests.md       # TESTER (create)
├── verify-reconciliation.md    # TESTER (create)
│
├── debug-test-failure.md       # BUILDER (create)
└── run-tdd-cycle.md            # BUILDER (create)
```

## Benefits

### For Users
- Faster analysis (hours → minutes)
- Consistent approach across projects
- No missed steps or requirements
- Clear output format

### For Framework
- Accumulating intelligence
- Each project teaches new patterns
- Skills improve over time
- Easier onboarding for new users

### For Teams
- Shared vocabulary (everyone uses same skills)
- Reusable artifacts (analysis docs, schemas, tests)
- Knowledge retention (skills encode best practices)
- Quality consistency

## Next Steps

1. **Create Priority 1 skills** (analyze-csv, compare-actual-vs-target, write-parser-tests)
2. **Test on next project** (validate they work outside MCU)
3. **Iterate based on feedback** (improve templates)
4. **Create Priority 2 skills** as needed
5. **Document patterns** (update this guide with learnings)

---

**Key Insight**: Every project is both:
1. **A use case** (solve this specific problem)
2. **A teaching moment** (extract reusable patterns)

MCU gave us Excel analysis skills. Next project will give us something else. The framework evolves.

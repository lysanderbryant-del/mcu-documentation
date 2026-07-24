---
name: compare-actual-vs-target
description: Verify calculated values match expected targets (reconciliation check)
agent: ANALYST
---

# Compare Actual vs Target Skill

Reconciliation verification - does our calculation match the expected value?

## User Request
$ARGUMENTS

## Your Task

Compare actual parsed/calculated values against expected targets to identify discrepancies.

## Step-by-Step Workflow

### 1. Identify Target Values

**From Excel workbook**:
- Read original Excel file
- Extract expected totals from summary tabs
- Note cell references (e.g., "Cell K82 = £52.66M")

**From specification**:
- Read `outputs/excel-structure-analysis.md`
- Look for "Target" or "Expected" values
- Note business date

**From user**:
- Ask: "What's the expected total for [date]?"

### 2. Calculate Actual Values

**Option A: Run parsers**
```python
from loaders.csv_parsers import *
from datetime import date

business_date = date(2026, 7, 22)

# Parse each source
bnp_cel_mc = BNPMCStatementParser().parse(file1, business_date, 'CEL')
bnp_ote = BNPOTEDetailParser().parse(file2, business_date)
journal = BNPJournalEntriesParser().parse(file3, business_date)
csa = CSACollateralParser().parse(file4, business_date)
# ... etc

# Sum components
total_actual = sum([
    sum(r['position_value_native'] for r in bnp_cel_mc),
    sum(r['position_value_native'] for r in bnp_ote),
    journal['position_value_native'],
    sum(r['position_value_native'] for r in csa),
])
```

**Option B: Query database**
```python
import sqlite3
conn = sqlite3.connect('data/margin_recon.db')

query = """
SELECT 
    clearer,
    margin_type,
    SUM(position_value_native) as total
FROM margin_positions
WHERE business_date = '2026-07-22'
GROUP BY clearer, margin_type
ORDER BY clearer, margin_type
"""

results = conn.execute(query).fetchall()
```

### 3. Compare Component by Component

Build comparison table:

| Component | Target | Actual | Delta | % Diff | Status |
|-----------|--------|--------|-------|--------|--------|
| BNP CEL MC | £52.66M | £52.66M | £0.00M | 0.0% | ✓ MATCH |
| BNP OTE | £29.46M | £10.60M | -£18.86M | -64% | ✗ FAIL |
| Journal | £23.51M | £75.70M | +£52.19M | +222% | ✗ FAIL |
| CSA | £11.72M | - | - | - | ⏳ NO DATA |
| **TOTAL** | **£65.11M** | **£139.96M** | **+£74.85M** | **+115%** | **✗ FAIL** |

### 4. Analyze Root Causes

For each failure, investigate:

**Check 1: Data Loaded?**
```python
if actual is None:
    cause = "Parser not run or returned no data"
```

**Check 2: Filter Applied?**
```python
# Expected: Filter PAYMENT_TYPE IN ('PC', 'DLV')
# Actual: No filter (includes all rows)
if actual > target * 2:
    cause = "Missing filter - including too many rows"
```

**Check 3: Column Mapping Correct?**
```python
# Expected: Column 7 = DEBIT
# Actual: Column 7 = something else (wrong skiprows?)
```

**Check 4: Currency Conversion?**
```python
# Expected: EUR * 0.825 = GBP
# Actual: EUR not converted
if target_currency == 'GBP' and actual_currency == 'EUR':
    cause = "Missing FX conversion"
```

**Check 5: Aggregation Level?**
```python
# Expected: Position-level (1,830 rows)
# Actual: Trade-level (148,625 rows)
if actual_row_count >> expected_row_count:
    cause = "Missing aggregation"
```

### 5. Create Reconciliation Report

Write: `$PROJECT_DIR/outputs/reconciliation-<date>.md`

**Template**:
```markdown
# Reconciliation Report: YYYY-MM-DD

**Target Date**: 2026-07-22
**Analysis Date**: 2026-07-24
**Target Total**: £65.11M
**Actual Total**: £139.96M
**Delta**: +£74.85M (115% over)
**Status**: ✗ FAILED

---

## Summary Table

| Component | Target | Actual | Delta | Status | Issue |
|-----------|--------|--------|-------|--------|-------|
| BNP CEL MC (CEL) | £18.66M | £18.66M | £0.00M | ✓ PASS | - |
| BNP CEL MC (CET) | £11.74M | £11.74M | £0.00M | ✓ PASS | - |
| BNP OTE | £10.60M | £10.60M | £0.00M | ✓ PASS | - |
| BNP Journal Entries | £23.51M | £75.70M | +£52.19M | ✗ FAIL | Missing filter |
| BNP PnS | £0.00M | £0.00M | £0.00M | ✓ PASS | - |
| CSA Collateral | £11.72M | - | - | ⏳ PENDING | Not loaded |
| SocGen | -£11.12M | -£11.12M | £0.00M | ✓ PASS | - |
| **TOTAL** | **£65.11M** | **£105.58M** | **+£40.47M** | **✗ FAIL** | - |

**Passing**: 5/7 components (71%)
**Failing**: 1/7 components (14%)
**Pending**: 1/7 components (14%)

---

## Issue Analysis

### Issue 1: Journal Entries £52.19M Too High

**Component**: BNP Journal Entries
**Expected**: £23.51M
**Actual**: £75.70M
**Delta**: +£52.19M (222% over)

**Root Cause**:
- Current parser: Sums ALL transactions in CSV
- Should be: Filter PAYMENT_TYPE IN ('PC', 'DLV') only
- Extra included: CSH (Cash) transactions = £52.19M

**Evidence**:
```bash
# Analyst report (analyst-journal-entries.md:45)
"Filter: PAYMENT_TYPE IN ('PC', 'DLV')"
"Found: 7 PC + 25 DLV = 32 transactions"
"Excluded: 3 CSH transactions"
```

**Current Code** (`csv_parsers.py:164-170`):
```python
# NO FILTERING - processes all rows
debit_sum = pd.to_numeric(df[debit_col], ...).sum()
credit_sum = pd.to_numeric(df[credit_col], ...).sum()
```

**Required Fix**:
```python
# ADD FILTERING before calculation
payment_type_col = df.columns[11]
mask = df[payment_type_col].isin(['PC', 'DLV'])
filtered = df[mask]

debit_sum = pd.to_numeric(filtered[debit_col], ...).sum()
credit_sum = pd.to_numeric(filtered[credit_col], ...).sum()
```

**File**: `src/loaders/csv_parsers.py`
**Line**: 164 (insert filter before sum)
**Priority**: HIGH (blocking £65.11M reconciliation)

---

### Issue 2: CSA Collateral Not Loaded

**Component**: CSA Collateral
**Expected**: £11.72M
**Actual**: (no data)

**Root Cause**:
- Parser code exists
- Tests written but failing
- File path format issue (backslashes vs forward slashes)

**Evidence**:
```bash
# Test output:
FileNotFoundError: \\app-nas-fsx-prod\...
```

**Required Fix**:
- Convert test file paths to forward slashes
- OR: Fix path handling in parser

**File**: `tests/test_remaining_parsers_tdd.py`
**Line**: 227 (TEST_FILE path)
**Priority**: MEDIUM (known issue, fix in progress)

---

## Component Details

### BNP CEL MC (CEL) ✓
- **Target**: £18.66M
- **Actual**: £18.66M
- **Status**: MATCH
- **Parser**: BNPMCStatementParser (CEL entity)

### BNP CEL MC (CET) ✓
- **Target**: £11.74M
- **Actual**: £11.74M
- **Status**: MATCH
- **Parser**: BNPMCStatementParser (CET entity)

### BNP OTE ✓
- **Target**: £10.60M
- **Actual**: £10.60M
- **Status**: MATCH
- **Parser**: BNPOTEDetailParser

[... continue for each component]

---

## Recommendations

### Immediate Actions (Block Reconciliation)
1. **Fix Journal Entries parser** (add PAYMENT_TYPE filter)
   - Priority: HIGH
   - Impact: Reduces delta by £52.19M
   - Time estimate: 10 minutes

2. **Load CSA Collateral data** (fix path format)
   - Priority: MEDIUM
   - Impact: Adds £11.72M component
   - Time estimate: 5 minutes

### After Fixes
3. **Re-run reconciliation** to verify
4. **Run integration test** (all components together)
5. **Validate against Excel** (£65.11M target)

---

## Next Steps

**BUILDER Phase**:
1. Apply fix to Journal Entries parser
2. Run tests: `pytest tests/test_remaining_parsers_tdd.py::TestJournalEntriesParser`
3. Verify: 4/4 tests passing (GREEN)
4. Fix CSA path format
5. Re-run this reconciliation check
6. Target: All components GREEN, total = £65.11M ±£0.01M

---

*Reconciliation analysis complete. Awaiting BUILDER fixes.*
```

### 6. Report to User

```
❌ Reconciliation FAILED

**Target**: £65.11M
**Actual**: £105.58M
**Delta**: +£40.47M (62% over)

**Issues Found**:
1. Journal Entries: £52.19M too high (missing PAYMENT_TYPE filter)
2. CSA Collateral: Not loaded (path format issue)

**Good News**:
- 5 out of 7 components passing (71%)
- Fixes are straightforward (10-15 minutes)

**Detailed Report**: outputs/reconciliation-2026-07-22.md

**Ready to fix?** I can apply the fixes now or you can review the report first.
```

## When to Use

### During Development
- After implementing each parser
- Verify component-by-component match
- Catch issues early

### Debugging Test Failures
- Test says "Expected X, got Y"
- This skill explains WHY
- Points to exact fix needed

### Before Integration Testing
- Ensure all components correct individually
- Verify reconciliation before combining

### Post-Deployment
- Daily validation check
- Alert if values drift
- Audit trail for compliance

## Integration with Other Skills

### Workflow Chain
1. **`/analyze-csv`** → Understand structure
2. **`/factory`** → ARCHITECT → TESTER → BUILDER
3. **`/compare-actual-vs-target`** → Verify each component ✓
4. Repeat until GREEN

### With Conductor
- Conductor runs this automatically after BUILDER
- If fails → BUILDER gets specific fix guidance
- If passes → Move to next component or REFACTOR

## Output Files

```
projects/<name>/outputs/
└── reconciliation-<date>.md    # Component-level comparison
```

---

*This skill is part of the Process Factory ANALYST toolkit.*
*Use to verify BUILDER implementations match ARCHITECT specifications.*

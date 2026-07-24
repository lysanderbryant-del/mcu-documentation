---
name: write-parser-tests
description: Generate TDD tests for CSV parsers (RED phase - tests will fail initially)
agent: TESTER
---

# Write Parser Tests Skill

Auto-generate failing tests (RED phase) for CSV parsers using TDD methodology.

## User Request
$ARGUMENTS

## Your Task

Write comprehensive failing tests BEFORE the parser is implemented (strict TDD).

## Step-by-Step Workflow

### 1. Gather Requirements

**Read ANALYST outputs**:
- `outputs/csv-analysis-<filename>.md` - Structure, columns, data types
- `outputs/analyst-<parser-name>.md` - Expected values, calculations

**Read ARCHITECT outputs**:
- `outputs/architect-<parser-name>.md` - Parser specification, algorithm

**Extract key info**:
- Expected output value (e.g., £23.51M)
- Expected structure (dict vs list)
- Edge cases to test (empty file, missing columns)
- Calculation formula

### 2. Determine Test Scenarios

**Core Tests** (Must Have):
1. **Structure test** - Returns correct format (dict/list)
2. **Calculation test** - Returns expected value
3. **Conversion test** - FX rate applied correctly (if applicable)
4. **Filter test** - Correct filtering logic (if applicable)

**Edge Case Tests** (Should Have):
5. **Empty file** - Handles gracefully
6. **Missing columns** - Raises appropriate error
7. **Invalid data** - Handles non-numeric values

**Integration Tests** (Nice to Have):
8. **Database insert** - No UNIQUE constraint errors
9. **Multiple files** - Processes batch correctly

### 3. Generate Test Class

**Template**:
```python
"""
TDD Tests for [Parser Name]

These tests are written BEFORE implementation (RED phase).
They WILL FAIL initially - this is expected and correct.

Test-Driven Development Cycle:
1. RED: Write failing test (this file)
2. GREEN: Make test pass (implement parser)
3. REFACTOR: Improve code quality

Based on:
- analyst-[name].md (expected values)
- architect-[name].md (design spec)
"""

import pytest
from datetime import date
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from loaders.csv_parsers import (
    [ParserClassName],
    ParseError
)


class Test[ParserName]:
    """
    TDD for [Parser Name]
    Target: [Expected value, e.g., £23.51M]
    """

    # Test file path (from network or local)
    TEST_FILE = Path('[network/path/to/file.csv]')
    TEST_DATE = date(YYYY, MM, DD)

    def test_returns_correct_structure(self):
        """
        RED TEST: Verify output format
        
        GIVEN: [File description]
        WHEN: Parser processes file
        THEN: Should return [dict/list] with required fields
        """
        parser = [ParserClassName]()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)
        
        # Check type
        assert isinstance(result, [dict/list]), "Should return [dict/list]"
        
        # Check required fields
        if isinstance(result, dict):
            required_fields = [
                'business_date',
                'clearer',
                'entity',
                'margin_type',
                'position_value_native',
                'original_currency',
                'source_file'
            ]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
        
        # Check field values
        assert result['business_date'] == self.TEST_DATE
        assert result['clearer'] == '[CLEARER_NAME]'
        assert result['original_currency'] == '[CURRENCY]'

    def test_calculates_correct_amount(self):
        """
        RED TEST: Verify calculation
        
        GIVEN: [Data description]
        WHEN: Parser calculates [metric]
        THEN: Should return [X] ± [tolerance]
        """
        parser = [ParserClassName]()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)
        
        amount = result['position_value_native']
        
        # Check value within tolerance
        EXPECTED = [value]  # e.g., 28_500_000 for €28.5M
        TOLERANCE = [value] # e.g., 100_000 for ±£0.1M
        
        assert (EXPECTED - TOLERANCE) <= amount <= (EXPECTED + TOLERANCE), \
            f"Expected {EXPECTED:,.0f} ±{TOLERANCE:,.0f}, got {amount:,.0f}"

    def test_applies_filter_correctly(self):
        """
        RED TEST: Verify filtering logic
        
        GIVEN: CSV with [N] rows including [filter criteria]
        WHEN: Parser filters by [column]
        THEN: Should include only [matching rows]
        """
        parser = [ParserClassName]()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)
        
        # Verification depends on output
        # Option A: Check margin_type indicates filter applied
        assert result['margin_type'] == '[EXPECTED_TYPE]'
        
        # Option B: If list returned, check row count
        # assert [X] <= len(result) <= [Y]

    def test_handles_empty_file(self):
        """
        RED TEST: Edge case - empty file
        
        GIVEN: Empty CSV file (0 bytes or only headers)
        WHEN: Parser attempts to process
        THEN: Should return empty result or raise ParseError
        """
        parser = [ParserClassName]()
        
        # Create empty test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            empty_file = Path(f.name)
        
        try:
            result = parser.parse(empty_file, self.TEST_DATE)
            # Should return empty structure
            if isinstance(result, dict):
                assert result['position_value_native'] == 0.0
            else:
                assert len(result) == 0
        except ParseError as e:
            # Also acceptable to raise error
            assert "empty" in str(e).lower()
        finally:
            empty_file.unlink()

    def test_handles_missing_columns(self):
        """
        RED TEST: Edge case - CSV missing required columns
        
        GIVEN: Malformed CSV (wrong structure)
        WHEN: Parser attempts to process
        THEN: Should raise ParseError with clear message
        """
        parser = [ParserClassName]()
        
        # Create malformed test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\nval1,val2\n")  # Wrong columns
            bad_file = Path(f.name)
        
        try:
            with pytest.raises(ParseError) as exc_info:
                parser.parse(bad_file, self.TEST_DATE)
            
            # Error message should be helpful
            assert "column" in str(exc_info.value).lower()
        finally:
            bad_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
```

### 4. Fill in Test Details

**From ANALYST report**, extract:
- Expected amount: "£23.51M" → `EXPECTED = 23_510_000`
- Tolerance: "±£0.01M" → `TOLERANCE = 10_000`
- Filter criteria: "PAYMENT_TYPE IN ('PC', 'DLV')"
- Data description: "32 transactions (7 PC + 25 DLV)"

**From ARCHITECT report**, extract:
- Return type: "Dict with keys: business_date, clearer, ..."
- Algorithm: "Filter by PAYMENT_TYPE, sum DEBIT - CREDIT"
- Edge cases: "Empty file → return 0.0"

### 5. Write Test File

Save to: `$PROJECT_DIR/tests/test_[parser_name]_tdd.py`

**Naming convention**:
- File: `test_bnp_journal_entries_tdd.py`
- Class: `TestBNPJournalEntries`
- Parser: `BNPJournalEntriesParser`

### 6. Run Tests (Expect RED)

```bash
cd $PROJECT_DIR
python -m pytest tests/test_[parser_name]_tdd.py -v

# Expected output:
# test_returns_correct_structure FAILED
# test_calculates_correct_amount FAILED
# test_applies_filter_correctly FAILED
# test_handles_empty_file FAILED
# test_handles_missing_columns FAILED
# 
# 0 passed, 5 failed - This is CORRECT for RED phase!
```

### 7. Create Test Report

Write: `$PROJECT_DIR/outputs/tests-[parser-name].md`

**Template**:
```markdown
# TDD Tests: [Parser Name]

**Date**: YYYY-MM-DD
**Phase**: RED (tests written, expected to fail)
**Parser**: [ParserClassName]
**Target**: [Expected value]

---

## Test Suite Overview

**File**: `tests/test_[parser_name]_tdd.py`
**Test Class**: `Test[ParserName]`
**Test Count**: 5 tests

### Test Categories

**Core Tests** (3):
1. ✓ test_returns_correct_structure - Verify output format
2. ✓ test_calculates_correct_amount - Verify calculation
3. ✓ test_applies_filter_correctly - Verify filtering

**Edge Case Tests** (2):
4. ✓ test_handles_empty_file - Empty/zero-size file
5. ✓ test_handles_missing_columns - Malformed CSV

---

## Test Details

### Test 1: Structure Validation

**Purpose**: Ensure parser returns correct format

**Expected Structure**:
```python
{
    'business_date': date(2026, 7, 22),
    'clearer': 'BNP',
    'entity': 'CEL',
    'margin_type': 'SPOT_PHYSICAL',
    'position_value_native': float,
    'original_currency': 'EUR',
    'source_file': str
}
```

**Assertion**: All required fields present with correct types

---

### Test 2: Calculation Validation

**Purpose**: Verify amount calculation

**Expected Value**: £23,510,000 ±£10,000
**Based On**: 
- Analyst report: "Net (DEBIT - CREDIT) = £23.51M"
- Filter: PAYMENT_TYPE IN ('PC', 'DLV')
- Rows: 32 transactions (7 PC + 25 DLV)

**Assertion**: 
```python
23_500_000 <= amount <= 23_520_000
```

---

### Test 3: Filter Validation

**Purpose**: Ensure correct filtering applied

**Filter Criteria**: PAYMENT_TYPE IN ('PC', 'DLV')
**Should Exclude**: CSH (Cash) transactions

**Verification**: 
- Margin type = 'SPOT_PHYSICAL' (indicates filter applied)
- Amount matches expected (would be higher if CSH included)

---

### Test 4: Empty File Handling

**Purpose**: Edge case - graceful failure

**Scenario**: Parser receives empty/zero-size file

**Expected Behavior**:
- Option A: Return `position_value_native = 0.0`
- Option B: Raise `ParseError("File is empty")`

Both acceptable - depends on ARCHITECT design

---

### Test 5: Missing Columns Handling

**Purpose**: Edge case - malformed CSV

**Scenario**: CSV missing required columns (wrong structure)

**Expected Behavior**:
- Raise `ParseError` with helpful message
- Message should mention "column" or "structure"

---

## Test Execution

### Initial Run (RED Phase)

```bash
pytest tests/test_[parser_name]_tdd.py -v

FAILED test_returns_correct_structure
FAILED test_calculates_correct_amount
FAILED test_applies_filter_correctly
FAILED test_handles_empty_file
FAILED test_handles_missing_columns

5 failed, 0 passed - EXPECTED (RED phase)
```

**Status**: ✗ All tests failing (correct for RED phase)

### After Implementation (GREEN Phase)

**Goal**: All tests passing

```bash
pytest tests/test_[parser_name]_tdd.py -v

PASSED test_returns_correct_structure
PASSED test_calculates_correct_amount
PASSED test_applies_filter_correctly
PASSED test_handles_empty_file
PASSED test_handles_missing_columns

5 passed, 0 failed - SUCCESS (GREEN phase)
```

---

## Next Steps

**BUILDER Phase**:
1. Implement `[ParserClassName].parse()` method
2. Run tests frequently (TDD: small iterations)
3. Fix one test at a time (RED → GREEN)
4. Refactor when all GREEN
5. Run `/compare-actual-vs-target` to verify

**RED → GREEN → REFACTOR cycle**

---

*Tests written. Ready for BUILDER implementation.*
```

### 8. Report to User

```
✓ TDD Tests Written (RED Phase)

**Parser**: [ParserClassName]
**Tests**: 5 tests created
**File**: tests/test_[parser_name]_tdd.py

**Test Coverage**:
- ✓ Structure validation
- ✓ Calculation (target: [value])
- ✓ Filter logic
- ✓ Empty file handling
- ✓ Missing columns handling

**Status**: All tests FAILING (expected - RED phase)

**Next**: BUILDER implements parser to make tests pass (GREEN phase)

Run tests: `pytest tests/test_[parser_name]_tdd.py -v`
```

## When to Use

### Start of BUILDER Phase
- TESTER writes failing tests FIRST
- BUILDER has clear acceptance criteria
- No ambiguity about "done"

### Before Refactoring
- Tests protect against breaking changes
- Refactor with confidence
- Tests stay GREEN throughout

### Adding New Parser
- Standard process: ANALYST → ARCHITECT → TESTER → BUILDER
- TESTER always runs before BUILDER

## Integration with Workflow

```
ANALYST → /analyze-csv → csv-analysis.md
    ↓
ARCHITECT → /design-parser-spec → architect-parser.md
    ↓
TESTER → /write-parser-tests → test_parser_tdd.py (RED)
    ↓
BUILDER → Implement parser → test_parser_tdd.py (GREEN)
    ↓
BUILDER → Refactor → test_parser_tdd.py (stay GREEN)
    ↓
ANALYST → /compare-actual-vs-target → reconciliation.md
```

## Output Files

```
projects/<name>/
├── tests/
│   └── test_[parser_name]_tdd.py    # Generated tests
└── outputs/
    └── tests-[parser-name].md       # Test documentation
```

---

*This skill is part of the Process Factory TESTER toolkit.*
*Pure TDD: Write failing tests FIRST, then make them pass.*

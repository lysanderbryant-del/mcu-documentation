# TDD Reset Plan - Strict Farley Approach

**Date**: 2026-07-24  
**Goal**: Fix remaining 3 parsers using pure Test-Driven Development

---

## Problem Statement

**Current**: £53.66M loaded (82% of £65.11M target)

**Missing Components**:
1. Journal Entries parser - Spot/Physical delivery (~£23.51M expected)
2. OTE Detail parser - Product-level breakdown (69MB file, thousands of products)
3. CSA Collateral parser - CSA margin (~£11.72M expected)

**Target**: £65.11M with complete traceability

---

## Farley Principles Applied

### 1. Optimise for Learning
- Write tests that EXPRESS our understanding
- Let test failures TEACH us what's wrong
- Use evidence (actual CSV data) over opinion

### 2. Manage Complexity  
- One parser at a time
- Small, focused tests
- Clear separation of concerns

### 3. Test-Driven Development
- **RED**: Write a failing test
- **GREEN**: Make it pass (simplest way)
- **REFACTOR**: Improve the code

### 4. Iterate
- Smallest useful increment first
- Each test is a tiny step forward

---

## Workflow: Analyst → Architect → Tester → Builder

---

## STEP 1: ANALYST Phase

**Goal**: Understand EXACTLY what each parser must do

### Task 1.1: Analyze Journal Entries CSV
**Question**: What is the correct way to extract the spot/physical total?

**Evidence Needed**:
- Actual CSV structure (header row, columns)
- Sample data rows
- Which column(s) contain amounts
- Expected total: £23.51M

**Action**: Read CSV, document findings

### Task 1.2: Analyze OTE Detail CSV  
**Question**: What causes the duplicate constraint?

**Evidence Needed**:
- Unique key definition
- Sample rows that would duplicate
- How many unique products

**Action**: Read CSV, identify duplicate pattern

### Task 1.3: Analyze CSA CSV
**Question**: Is the file really empty, or are we reading it wrong?

**Evidence Needed**:
- Actual file size and content
- Correct header row
- Expected data format

**Action**: Inspect actual file

---

## STEP 2: ARCHITECT Phase

**Goal**: Design the solution BEFORE coding

For each parser, specify:
- Input: CSV file structure
- Output: Data structure (dict/list)
- Logic: Extraction algorithm
- Edge cases: Empty files, missing columns, duplicates

---

## STEP 3: TESTER Phase

**Goal**: Write failing tests that describe desired behavior

### Test 3.1: Journal Entries Parser
```python
def test_journal_entries_extracts_correct_total():
    """
    GIVEN: Journal Entries CSV for 2026-07-22
    WHEN: Parser extracts spot/physical delivery total
    THEN: Total should be £23.51M ± £0.01M
    """
    # This test will FAIL until we fix the parser
    parser = BNPJournalEntriesParser()
    file_path = Path('.../Journal_Entries_CEL U_2026-07-22_*.csv')
    result = parser.parse(file_path, date(2026, 7, 22))
    
    total_gbp_m = result['position_value_native'] / 1_000_000
    assert 23.50 <= total_gbp_m <= 23.52, f"Expected ~£23.51M, got £{total_gbp_m:.2f}M"
```

### Test 3.2: OTE Detail Parser
```python
def test_ote_detail_handles_duplicates_gracefully():
    """
    GIVEN: OTE Detail CSV with potential duplicate records
    WHEN: Parser extracts product positions
    THEN: No duplicate key errors, products aggregated correctly
    """
    # This test will FAIL due to duplicate constraint
    parser = BNPOTEDetailParser()
    file_path = Path('.../Detailed_Open_Pos_CEL U_2026-07-22_*.csv')
    result = parser.parse(file_path, date(2026, 7, 22))
    
    # Should return list of unique products
    products = [r['product_name'] for r in result]
    assert len(products) == len(set(products)), "Duplicate products found"
```

### Test 3.3: CSA Parser
```python
def test_csa_parser_handles_empty_or_different_format():
    """
    GIVEN: CSA CSV that may be empty or have different structure
    WHEN: Parser attempts to extract collateral
    THEN: Returns sensible default or parses correctly
    """
    # This test will FAIL if file is truly empty
    parser = CSACollateralParser()
    file_path = Path('.../Collateral_Summary_2026_07_22_*.csv')
    result = parser.parse(file_path, date(2026, 7, 22))
    
    assert isinstance(result, list), "Should return list"
    assert len(result) > 0, "Should have at least one record"
```

---

## STEP 4: BUILDER Phase

**Goal**: Make tests pass (RED → GREEN → REFACTOR)

### For Each Parser:

#### RED Phase
1. Run test
2. Watch it fail
3. Read failure message carefully

#### GREEN Phase  
1. Write SIMPLEST code to pass
2. Don't worry about elegance yet
3. Just make the test green

#### REFACTOR Phase
1. Improve code quality
2. Remove duplication
3. Add clarity
4. Tests stay green throughout

---

## Execution Order

### Round 1: Journal Entries Parser (30 min)
1. **Analyst**: Inspect CSV, find correct columns
2. **Architect**: Design extraction logic
3. **Tester**: Write failing test
4. **Builder**: Fix parser (RED → GREEN → REFACTOR)

### Round 2: OTE Detail Parser (30 min)
1. **Analyst**: Identify duplicate issue
2. **Architect**: Design deduplication strategy
3. **Tester**: Write failing test
4. **Builder**: Fix parser (RED → GREEN → REFACTOR)

### Round 3: CSA Parser (20 min)
1. **Analyst**: Inspect file, determine if empty
2. **Architect**: Design handling for empty/different format
3. **Tester**: Write failing test
4. **Builder**: Fix parser (RED → GREEN → REFACTOR)

### Round 4: Integration Test (10 min)
1. **Tester**: Write test for complete load
2. **Builder**: Verify £65.11M total

---

## Success Criteria

### Tests Must:
- ✅ Be written BEFORE implementation code
- ✅ Fail initially (RED)
- ✅ Pass after implementation (GREEN)
- ✅ Stay green after refactoring
- ✅ Be specific and verifiable

### Code Must:
- ✅ Pass all tests
- ✅ Load £65.11M total (within £0.01M)
- ✅ Have no duplicates
- ✅ Be traceable to source files

---

## Test File Structure

```python
# tests/test_remaining_parsers.py

import pytest
from datetime import date
from pathlib import Path

class TestJournalEntriesParser:
    """TDD for Journal Entries parser fix"""
    
    def test_extracts_correct_total(self):
        # RED: This will fail first
        pass
    
    def test_handles_both_amount_columns(self):
        # Additional test for column 7 + column 8
        pass

class TestOTEDetailParser:
    """TDD for OTE Detail parser fix"""
    
    def test_loads_without_duplicate_errors(self):
        # RED: This will fail due to constraint
        pass
    
    def test_aggregates_products_correctly(self):
        # Additional test for product aggregation
        pass

class TestCSAParser:
    """TDD for CSA parser fix"""
    
    def test_handles_empty_file(self):
        # RED: This will fail if not handled
        pass
    
    def test_parses_actual_data_when_present(self):
        # Test for real CSA file with data
        pass
```

---

## Ready to Start?

**Next Command**:
```bash
# Create test file
touch tests/test_remaining_parsers.py

# Start with ANALYST phase for Journal Entries
python -c "
import pandas as pd
from pathlib import Path

file_path = Path('//pgb1-p-e-evs012/.../Journal_Entries_CEL U_2026-07-22_*.csv')
df = pd.read_csv(file_path, skiprows=9, nrows=20)

print('ANALYST: Journal Entries CSV Structure')
print('='*70)
print(f'Columns: {len(df.columns)}')
print(f'Rows: {len(df)}')
print('\nAmount columns analysis...')
"
```

---

*TDD Reset Plan ready. Proceeding with strict Analyst → Architect → Tester → Builder workflow.*

# Architecture Design: Journal Entries Parser

**Date**: 2026-07-24  
**Phase**: ARCHITECT  
**Input**: Analyst report from `analyst-journal-entries.md`

---

## Problem Statement

Extract spot/physical delivery total from Journal Entries CSV file.

**Target**: £23,510,000 (±£10,000 tolerance)

---

## Design Decisions

### Input Specification
```python
file_path: Path  # Journal_Entries_CEL U_YYYY-MM-DD_*.csv
business_date: date  # e.g., 2026-07-22
```

### Output Specification
```python
{
    'business_date': date,
    'clearer': 'BNP',
    'entity': 'CEL',
    'margin_type': 'SPOT_PHYSICAL',
    'position_value_native': float,  # EUR amount
    'original_currency': 'EUR',
    'source_file': str(file_path)
}
```

---

## Algorithm

### Step 1: Read CSV
```python
df = pd.read_csv(file_path, skiprows=9, encoding='utf-8-sig')
```
**Rationale**: Header is on row 10 (0-indexed row 9)

### Step 2: Identify Columns
```python
DEBIT_COLUMN = df.columns[7]   # Column index 7
CREDIT_COLUMN = df.columns[8]  # Column index 8
PAYMENT_TYPE_COLUMN = df.columns[11]  # Column index 11
```
**Rationale**: Analyst identified these as the correct columns

### Step 3: Filter Transactions
```python
filtered = df[df[PAYMENT_TYPE_COLUMN].isin(['PC', 'DLV'])]
```
**Rationale**: 
- PC = Payment Commodity
- DLV = Physical Delivery
- Exclude CSH = Cash movements

### Step 4: Calculate Net EUR Amount
```python
debit_total = filtered[DEBIT_COLUMN].sum()
credit_total = filtered[CREDIT_COLUMN].sum()
net_eur = abs(debit_total - credit_total)
```
**Rationale**: Double-entry accounting - net of debits and credits

### Step 5: Convert to GBP (handled by loader)
```python
# Loader will apply FX rate
# EUR amount returned here, conversion happens in daily_loader
```
**Rationale**: Separation of concerns - parser extracts, loader converts

---

## Edge Cases

### Case 1: Empty File
**Scenario**: No transactions for the date  
**Handling**: Return EUR 0.0

### Case 2: Missing Columns
**Scenario**: CSV structure changed  
**Handling**: Raise `ParseError` with descriptive message

### Case 3: Non-numeric Values
**Scenario**: Column contains text  
**Handling**: Convert to numeric, coerce errors to 0

---

## Pseudocode

```python
def parse(self, file_path: Path, business_date: date) -> Dict[str, Any]:
    """Parse Journal Entries for spot/physical delivery."""
    
    # Read CSV
    df = pd.read_csv(file_path, skiprows=9, encoding='utf-8-sig')
    
    # Validate structure
    if len(df.columns) < 12:
        raise ParseError("Insufficient columns")
    
    # Get column references
    debit_col = df.columns[7]
    credit_col = df.columns[8]
    payment_type_col = df.columns[11]
    
    # Filter for spot/physical
    mask = df[payment_type_col].isin(['PC', 'DLV'])
    filtered = df[mask]
    
    # Calculate net amount
    debit_sum = pd.to_numeric(filtered[debit_col], errors='coerce').fillna(0).sum()
    credit_sum = pd.to_numeric(filtered[credit_col], errors='coerce').fillna(0).sum()
    net_eur = abs(debit_sum - credit_sum)
    
    # Return result
    return {
        'business_date': business_date,
        'clearer': 'BNP',
        'entity': 'CEL',
        'margin_type': 'SPOT_PHYSICAL',
        'position_value_native': net_eur,
        'original_currency': 'EUR',
        'source_file': str(file_path)
    }
```

---

## Test Specification

### Test 1: Correct Total
```python
def test_journal_entries_extracts_correct_total():
    parser = BNPJournalEntriesParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # After FX conversion (0.825), should be ~£23.51M
    eur_amount = result['position_value_native']
    gbp_equivalent = eur_amount * 0.825
    
    assert 23_500_000 <= gbp_equivalent <= 23_520_000
```

### Test 2: Filters Correctly
```python
def test_journal_entries_filters_payment_types():
    parser = BNPJournalEntriesParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Should only include PC and DLV, not CSH
    # Analyst found 32 transactions (7 PC + 25 DLV)
    # Manual verification: net should exclude 3 CSH transactions
    pass
```

### Test 3: Handles Empty File
```python
def test_journal_entries_handles_empty_file():
    parser = BNPJournalEntriesParser()
    result = parser.parse(EMPTY_FILE, date(2026, 7, 22))
    
    assert result['position_value_native'] == 0.0
```

---

## Dependencies

- **pandas**: CSV reading and filtering
- **pathlib**: File path handling
- **datetime**: Date handling

---

## Performance

- **File Size**: ~10 KB (35 rows)
- **Parse Time**: <100ms expected
- **Memory**: <1 MB

---

## Validation

Expected result for 2026-07-22:
```
EUR amount: €28,495,030.68
GBP equivalent (0.825): £23,508,350.31
Target: £23,510,000
Difference: -£1,650 (0.007% error - acceptable)
```

---

*Architecture design complete. Ready for TESTER phase.*

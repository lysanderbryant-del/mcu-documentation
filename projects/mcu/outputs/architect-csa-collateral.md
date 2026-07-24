# Architecture Design: CSA Collateral Parser

**Date**: 2026-07-24  
**Phase**: ARCHITECT  
**Input**: Analyst report from `analyst-csa-collateral.md`

---

## Problem Statement

Parse CSA Collateral Summary CSV containing net collateral positions by entity and counterparty.

**Current Issue**: Parser using wrong `skiprows` and incorrect column names

---

## Design Decisions

### Input Specification
```python
file_path: Path  # Collateral_Summary_YYYY_MM_DD_*.csv
business_date: date
```

### Output Specification
```python
List[Dict[str, Any]]  # One record per entity-currency combination

Each record:
{
    'business_date': date,
    'clearer': 'CSA',
    'entity': 'CEL' or 'CET',
    'margin_type': 'COLLATERAL',
    'counterparty': str,  # Trading counterparty name
    'original_currency': str,
    'position_value_native': float,  # Net collateral (Held - Pledged)
    'source_file': str
}
```

---

## Algorithm

### Step 1: Read CSV (CORRECTED)
```python
df = pd.read_csv(file_path, skiprows=0, encoding='utf-8-sig')  # NOT skiprows=6!
```
**Rationale**: Analyst found header is on line 1, no rows to skip

### Step 2: Validate Structure
```python
required_columns = [
    'Our_Entity',
    'Trading_Counterparty',
    'Collateral_Type',
    'Reporting_Currency',
    'Collateral_Held',    # NOT HeldGbpM
    'Collateral_Pledged'  # NOT PledgedGbpM
]

if not all(col in df.columns for col in required_columns):
    raise ParseError("Missing required columns")
```

### Step 3: Filter for Centrica Entities
```python
entity_map = {
    'Centrica Energy Limited': 'CEL',
    'Centrica Energy Trading A/S': 'CET'  # Note: includes "A/S"
}

df_filtered = df[df['Our_Entity'].isin(entity_map.keys())]
```
**Rationale**: Analyst found exact entity names in file

### Step 4: Calculate Net Collateral
```python
df_filtered['net_collateral'] = (
    df_filtered['Collateral_Held'] - df_filtered['Collateral_Pledged']
)
```
**Rationale**: Net = What we hold minus what we pledged

### Step 5: Aggregate by Entity and Currency
```python
aggregated = df_filtered.groupby([
    'Our_Entity',
    'Reporting_Currency'
]).agg({
    'net_collateral': 'sum',
    'Trading_Counterparty': lambda x: ', '.join(x.unique())  # List all counterparties
}).reset_index()
```

### Step 6: Transform to Output Format (NO SCALING)
```python
result = []
for _, row in aggregated.iterrows():
    result.append({
        'business_date': business_date,
        'clearer': 'CSA',
        'entity': entity_map[row['Our_Entity']],
        'margin_type': 'COLLATERAL',
        'counterparty': row['Trading_Counterparty'],
        'original_currency': row['Reporting_Currency'],
        'position_value_native': row['net_collateral'],  # Already in native units
        'source_file': str(file_path)
    })
```
**Rationale**: Analyst found values are already in native currency units, NOT millions

---

## Edge Cases

### Case 1: Empty File
**Scenario**: File exists but has no data rows  
**Handling**: Return empty list `[]`

### Case 2: Missing Entity
**Scenario**: Only CEL present, no CET  
**Handling**: Return records for present entities only

### Case 3: Multiple Files Available
**Scenario**: Two files per day (05:15 and 07:40)  
**Handling**: File discovery should prefer 07:40 file (latest)

---

## Pseudocode

```python
def parse(self, file_path: Path, business_date: date) -> List[Dict[str, Any]]:
    """Parse CSA Collateral Summary."""
    
    # Check file size
    if file_path.stat().st_size == 0:
        return []  # Empty file, return empty list
    
    # Read CSV (CORRECTED: skiprows=0, not 6)
    df = pd.read_csv(file_path, skiprows=0, encoding='utf-8-sig')
    
    # Validate columns exist
    required = ['Our_Entity', 'Collateral_Held', 'Collateral_Pledged', 'Reporting_Currency']
    if not all(col in df.columns for col in required):
        raise ParseError(f"Missing columns. Expected: {required}, Got: {list(df.columns)}")
    
    # Filter for Centrica entities
    entity_map = {
        'Centrica Energy Limited': 'CEL',
        'Centrica Energy Trading A/S': 'CET'
    }
    df_filtered = df[df['Our_Entity'].isin(entity_map.keys())]
    
    if len(df_filtered) == 0:
        return []  # No Centrica data
    
    # Calculate net collateral
    df_filtered['net_collateral'] = (
        df_filtered['Collateral_Held'] - df_filtered['Collateral_Pledged']
    )
    
    # Aggregate by entity and currency
    aggregated = df_filtered.groupby([
        'Our_Entity',
        'Reporting_Currency'
    ]).agg({
        'net_collateral': 'sum',
        'Trading_Counterparty': lambda x: ', '.join(x.unique())
    }).reset_index()
    
    # Transform to output
    result = []
    for _, row in aggregated.iterrows():
        result.append({
            'business_date': business_date,
            'clearer': 'CSA',
            'entity': entity_map[row['Our_Entity']],
            'margin_type': 'COLLATERAL',
            'counterparty': row['Trading_Counterparty'],
            'original_currency': row['Reporting_Currency'],
            'position_value_native': row['net_collateral'],
            'source_file': str(file_path)
        })
    
    return result
```

---

## Test Specification

### Test 1: Correct skiprows Value
```python
def test_csa_uses_correct_skiprows():
    parser = CSACollateralParser()
    
    # Should read header from line 1
    df = pd.read_csv(TEST_FILE, skiprows=0)
    assert 'Our_Entity' in df.columns
    assert 'Collateral_Held' in df.columns
```

### Test 2: Correct Column Names
```python
def test_csa_uses_correct_column_names():
    parser = CSACollateralParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Should successfully parse without KeyError
    assert isinstance(result, list)
    assert len(result) > 0
```

### Test 3: Entity Name Matching
```python
def test_csa_matches_entity_names_correctly():
    parser = CSACollateralParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Should find both CEL and CET if present
    entities = [r['entity'] for r in result]
    assert 'CEL' in entities or 'CET' in entities
```

### Test 4: Net Collateral Calculation
```python
def test_csa_calculates_net_collateral():
    parser = CSACollateralParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Net = Held - Pledged
    # Analyst found sample: Held=50, Pledged=30 → Net=20
    for record in result:
        assert 'position_value_native' in record
        # Value can be positive (we hold more) or negative (we pledged more)
```

### Test 5: No Scaling Applied
```python
def test_csa_does_not_multiply_by_million():
    parser = CSACollateralParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Values should be in native units, not millions
    # Analyst found typical values: 10,000 to 100,000, not 10 to 100
    for record in result:
        value = abs(record['position_value_native'])
        assert value > 1000, "Values seem too small, may be incorrectly scaled"
```

### Test 6: Handles Empty File
```python
def test_csa_handles_empty_file():
    parser = CSACollateralParser()
    
    # Create empty file
    empty_file = Path('test_empty.csv')
    empty_file.write_text('')
    
    result = parser.parse(empty_file, date(2026, 7, 22))
    assert result == []
```

---

## Performance

- **File Size**: 4.2 KB (50 rows)
- **Parse Time**: <50ms expected
- **Memory**: <1 MB

---

## File Selection Strategy

Analyst found two files per day:
- `Collateral_Summary_2026_07_22_051501.csv` (generated 05:15)
- `Collateral_Summary_2026_07_22_074004.csv` (generated 07:40)

**Recommendation**: Update file discovery to prefer latest (07:40) file for consistency with BNP file timing.

```python
# In file_discovery.py
def _find_csa_collateral(self):
    directory = self.csa_dir
    pattern = f'Collateral_Summary_{self.date_underscore}_*.csv'
    
    # Find latest file (not earliest)
    matches = list(directory.glob(pattern))
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)  # Latest by timestamp
```

---

*Architecture design complete. Ready for TESTER phase.*

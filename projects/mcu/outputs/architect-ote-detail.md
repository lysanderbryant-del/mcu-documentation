# Architecture Design: OTE Detail Parser

**Date**: 2026-07-24  
**Phase**: ARCHITECT  
**Input**: Analyst report from `analyst-ote-detail.md`

---

## Problem Statement

Parse 69MB OTE Detail CSV containing 148,625 trade-level rows and aggregate into ~1,830 unique position records for database insertion.

**Challenge**: Avoid UNIQUE constraint violations

---

## Design Decisions

### Input Specification
```python
file_path: Path  # Detailed_Open_Pos_CEL U_YYYY-MM-DD_*.csv
business_date: date
```

### Output Specification
```python
List[Dict[str, Any]]  # List of aggregated positions

Each position:
{
    'business_date': date,
    'clearer': 'BNP',
    'entity': 'CEL',
    'margin_type': 'OTE',
    'counterparty': 'BNP',
    'product_name': str,
    'commodity': str,
    'original_currency': str,
    'position_value_native': float,  # Aggregated OTE
    'maturity_date': date,  # NEW: needed for uniqueness
    'source_file': str
}
```

---

## Algorithm

### Step 1: Read CSV
```python
df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
```
**Rationale**: Large file (69MB), need low_memory=False to handle mixed types

### Step 2: Identify Aggregation Key
```python
group_by_columns = [
    'PRODUCT',           # Product name
    'CURRENCY',          # Currency code
    'MATURITY_DATE',     # Contract maturity
    'COMMODITY',         # Commodity type (if exists)
]
```
**Rationale**: Analyst found these define unique positions

### Step 3: Aggregate Trades into Positions
```python
aggregated = df.groupby(group_by_columns, dropna=False).agg({
    'QTY': 'sum',        # Sum quantities
    'OTE': 'sum',        # Sum open trade equity
    'VM': 'sum'          # Sum variation margin
}).reset_index()
```
**Rationale**: Multiple trades for same position must be summed

### Step 4: Transform to Output Format
```python
result = []
for _, row in aggregated.iterrows():
    result.append({
        'business_date': business_date,
        'clearer': 'BNP',
        'entity': 'CEL',
        'margin_type': 'OTE',
        'counterparty': 'BNP',
        'product_name': row['PRODUCT'],
        'commodity': row.get('COMMODITY', infer_from_product(row['PRODUCT'])),
        'original_currency': row['CURRENCY'],
        'position_value_native': row['OTE'],
        'maturity_date': row['MATURITY_DATE'],
        'source_file': str(file_path)
    })
```

---

## Edge Cases

### Case 1: Missing Commodity Column
**Scenario**: CSV doesn't have explicit commodity  
**Handling**: Infer from product name (e.g., "ICE TTF" → "GAS")

### Case 2: Mixed Data Types in Columns
**Scenario**: Pandas warning about mixed types  
**Handling**: Use `low_memory=False`, convert columns explicitly

### Case 3: NULL Maturity Dates
**Scenario**: Some products don't have maturity  
**Handling**: Use `dropna=False` in groupby, treat NULL as valid key

---

## Pseudocode

```python
def parse(self, file_path: Path, business_date: date) -> List[Dict[str, Any]]:
    """Parse OTE Detail with aggregation."""
    
    # Read CSV (large file)
    df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
    
    # Identify required columns
    product_col = find_column(df, ['PRODUCT', 'EXCHANGE_PRODUCT_DESCRIPTION'])
    ote_col = find_column(df, ['OTE', 'OPEN_TRADE_EQUITY'])
    currency_col = find_column(df, ['CURRENCY', 'ORIGINAL_CURRENCY'])
    maturity_col = find_column(df, ['MATURITY_DATE', 'EXPIRY_DATE'])
    
    # Aggregate by key columns
    group_cols = [product_col, currency_col, maturity_col]
    aggregated = df.groupby(group_cols, dropna=False).agg({
        ote_col: 'sum'
    }).reset_index()
    
    # Transform to output format
    result = []
    for _, row in aggregated.iterrows():
        result.append({
            'business_date': business_date,
            'clearer': 'BNP',
            'entity': 'CEL',
            'margin_type': 'OTE',
            'counterparty': 'BNP',
            'product_name': row[product_col],
            'original_currency': row[currency_col],
            'position_value_native': row[ote_col],
            'maturity_date': row[maturity_col],
            'commodity': infer_commodity(row[product_col]),
            'source_file': str(file_path)
        })
    
    return result
```

---

## Database Schema Update Required

**Current Unique Constraint**:
```sql
UNIQUE(business_date, clearer, margin_type, entity, counterparty, original_currency, product)
```

**Needs to Include**:
```sql
UNIQUE(business_date, clearer, margin_type, entity, counterparty, original_currency, product, maturity_date)
```

**Rationale**: Same product can have multiple maturities on same date

---

## Test Specification

### Test 1: Aggregation Reduces Row Count
```python
def test_ote_detail_aggregates_trades():
    parser = BNPOTEDetailParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Analyst found 148,625 rows → ~1,830 positions
    assert 1_800 <= len(result) <= 1_900
```

### Test 2: No Duplicate Keys
```python
def test_ote_detail_no_duplicates():
    parser = BNPOTEDetailParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Check for duplicates on key columns
    keys = [(r['product_name'], r['original_currency'], r['maturity_date']) 
            for r in result]
    assert len(keys) == len(set(keys)), "Duplicate positions found"
```

### Test 3: Correct Product Distribution
```python
def test_ote_detail_product_distribution():
    parser = BNPOTEDetailParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    # Analyst found ICETFM_F (ICE TTF) dominates with 62K trades
    icetfm_positions = [r for r in result if 'ICETFM' in r['product_name']]
    assert len(icetfm_positions) > 100  # Should have many maturities
```

### Test 4: Database Insert Succeeds
```python
def test_ote_detail_database_insert_no_constraint_error():
    parser = BNPOTEDetailParser()
    result = parser.parse(TEST_FILE, date(2026, 7, 22))
    
    db = DatabaseConnection('test.db')
    for record in result:
        db.store_margin_position(**record)  # Should not raise UNIQUE constraint
```

---

## Performance

- **File Size**: 69 MB
- **Input Rows**: 148,625
- **Output Rows**: ~1,830
- **Reduction**: 98.8%
- **Parse Time**: 5-10 seconds expected
- **Memory**: ~200 MB peak

---

## Commodity Inference Logic

```python
def infer_commodity(product_name: str) -> str:
    """Infer commodity from product name."""
    product_upper = product_name.upper()
    
    if any(x in product_upper for x in ['TTF', 'NBP', 'JKM', 'GAS', 'TFM', 'TFU']):
        return 'GAS'
    elif 'POWER' in product_upper or any(x in product_upper for x in ['GAB', 'GNM', 'GXC']):
        return 'POWER'
    elif any(x in product_upper for x in ['EUA', 'UKA', 'CARBON']):
        return 'EMISSIONS'
    elif any(x in product_upper for x in ['BRENT', 'OIL', 'GASOIL']):
        return 'OIL'
    elif 'COAL' in product_upper:
        return 'COAL'
    else:
        return 'OTHER'
```

---

*Architecture design complete. Ready for TESTER phase.*

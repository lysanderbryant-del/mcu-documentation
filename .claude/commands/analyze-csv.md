---
name: analyze-csv
description: Inspect CSV file structure (columns, types, sample data) without loading entire file
agent: ANALYST
---

# Analyze CSV Skill

Quick structural analysis of any CSV file.

## User Request
$ARGUMENTS

## Your Task

Analyze a CSV file to understand its structure before writing a parser.

## Step-by-Step Workflow

### 1. Get File Path
User provides: `path/to/file.csv`

If not provided, ask: "Which CSV file should I analyze?"

### 2. Determine Project Context
```bash
# Usually in a project context
PROJECT_DIR=projects/mcu  # or current project

# Create outputs if needed
mkdir -p $PROJECT_DIR/outputs
```

### 3. Quick File Check
```bash
FILE_PATH="$USER_PROVIDED_PATH"

# File size
FILE_SIZE=$(du -h "$FILE_PATH" | cut -f1)

# Row count (fast estimate)
ROW_COUNT=$(wc -l < "$FILE_PATH")

# First 20 lines (headers + sample)
head -20 "$FILE_PATH" > /tmp/csv_sample.txt
```

### 4. Detect Structure

**Find header row**:
```bash
# Often header is not on line 1
# Look for row with column names vs data
head -20 "$FILE_PATH"
```

**Detect delimiter**:
- Comma: `value1,value2,value3`
- Tab: `value1	value2	value3`
- Semicolon: `value1;value2;value3`
- Pipe: `value1|value2|value3`

**Count columns**:
```bash
head -1 "$FILE_PATH" | awk -F',' '{print NF}'
```

### 5. Analyze Column Types

Read first 100 data rows with pandas:
```python
import pandas as pd

# Try different skiprows values
for skip in [0, 1, 5, 9]:
    try:
        df = pd.read_csv(filepath, skiprows=skip, nrows=100)
        if df.shape[1] > 1:  # Found valid data
            break
    except:
        continue

# Column analysis
for col in df.columns:
    sample_values = df[col].dropna().head(5)
    dtype = df[col].dtype
    
    # Detect type
    if dtype in ['int64', 'float64']:
        col_type = 'Numeric'
    elif pd.to_datetime(df[col], errors='coerce').notna().sum() > 0:
        col_type = 'Date'
    else:
        col_type = 'Text'
    
    print(f"{col}: {col_type} - {list(sample_values)}")
```

### 6. Identify Issues

Check for:
- **Mixed types**: Column has both numbers and text
- **Missing values**: Large % of NULLs
- **Empty rows**: All columns empty
- **Duplicate headers**: Same column name twice
- **Special characters**: €, £, $ in numeric columns
- **Date formats**: DD/MM/YYYY vs YYYY-MM-DD

### 7. Create Analysis Report

Write: `$PROJECT_DIR/outputs/csv-analysis-<filename>.md`

**Template**:
```markdown
# CSV Analysis: [filename.csv]

**Date**: YYYY-MM-DD
**Project**: [project-name]
**Analyst**: ANALYST Agent

---

## File Overview

- **Path**: `path/to/file.csv`
- **Size**: 145 KB
- **Rows**: ~1,500 (estimated)
- **Delimiter**: comma (,)
- **Encoding**: UTF-8

## Structure

**Header Location**: Row 10 (skiprows=9)
**Data Starts**: Row 11
**Columns**: 15

## Column Details

| # | Name | Type | Sample Values | Issues |
|---|------|------|---------------|--------|
| 1 | (empty) | Index | 1, 2, 3, 4, 5 | - |
| 2 | ACCOUNT_NUMBER | Text | ACC001, ACC002, ACC003 | - |
| 3 | ACCOUNT_NAME | Text | Cash Account, Trading Account | - |
| 7 | DEBIT_AMOUNT | Numeric | 50000.00, 125000.50, 0.00 | - |
| 8 | CREDIT_AMOUNT | Numeric | 0.00, 25000.00, 10000.00 | - |
| 11 | PAYMENT_TYPE | Text | PC, DLV, CSH | 3 unique values |
| 15 | NOTES | Text | (mostly empty) | 95% NULL |

## Sample Data (First 5 Rows)

```csv
Row 11: DEBIT=50000.00, CREDIT=0.00, TYPE=PC
Row 12: DEBIT=0.00, CREDIT=25000.00, TYPE=DLV
Row 13: DEBIT=125000.50, CREDIT=0.00, TYPE=PC
Row 14: DEBIT=0.00, CREDIT=10000.00, TYPE=CSH
Row 15: DEBIT=75000.00, CREDIT=0.00, TYPE=DLV
```

## Issues Found

### Issue 1: Empty first column
**Impact**: Can ignore during parsing
**Fix**: Skip column 0 when mapping

### Issue 2: Mixed data in Notes column
**Impact**: Low (mostly empty anyway)
**Fix**: Treat as optional text field

### Issue 3: Header not on line 1
**Impact**: Must use skiprows=9
**Fix**: Ensure parser uses `pd.read_csv(file, skiprows=9)`

## Key Findings for Parser

### Filtering Logic Needed
- Column 11 (PAYMENT_TYPE) has 3 values: PC, DLV, CSH
- Likely need to filter specific types

### Calculation Candidates
- Columns 7 & 8 (DEBIT/CREDIT) are numeric
- Possible calculation: `net = DEBIT - CREDIT` or `abs(DEBIT - CREDIT)`

### Data Quality
- **Good**: No mixed types in numeric columns
- **Good**: Date format consistent
- **Caution**: 95% of NOTES column is empty
- **Caution**: 3 rows are completely empty (can filter)

## Recommended Parser Approach

```python
import pandas as pd

def parse(file_path, business_date):
    # Read with correct skiprows
    df = pd.read_csv(file_path, skiprows=9, encoding='utf-8-sig')
    
    # Filter for specific payment types (if needed)
    # mask = df[df.columns[11]].isin(['PC', 'DLV'])
    # df = df[mask]
    
    # Calculate net amount
    debit = pd.to_numeric(df[df.columns[7]], errors='coerce').fillna(0)
    credit = pd.to_numeric(df[df.columns[8]], errors='coerce').fillna(0)
    net = abs(debit.sum() - credit.sum())
    
    return {
        'business_date': business_date,
        'position_value_native': net,
        # ... other fields
    }
```

## Next Steps

1. ✓ Structure understood
2. [ ] Clarify: Should we filter PAYMENT_TYPE? Which values?
3. [ ] Clarify: Is net = DEBIT - CREDIT or ABS(DEBIT - CREDIT)?
4. [ ] ARCHITECT: Design parser specification
5. [ ] TESTER: Write failing tests
6. [ ] BUILDER: Implement parser

---

*Analysis complete. Ready for ARCHITECT phase.*
```

### 8. Report to User

```
✓ CSV Analysis Complete

**File**: filename.csv
**Size**: 145 KB (~1,500 rows)
**Structure**: 15 columns, header on row 10

**Key Findings**:
- Numeric columns: DEBIT_AMOUNT (col 7), CREDIT_AMOUNT (col 8)
- Filter column: PAYMENT_TYPE (col 11) with values PC, DLV, CSH
- Issues: 3 empty rows, header not on line 1

**Report**: outputs/csv-analysis-filename.md

**Questions for you**:
1. Should we filter PAYMENT_TYPE? Which values to include?
2. Is calculation: net = DEBIT - CREDIT or ABS()?

Ready for ARCHITECT phase when you confirm.
```

## When to Use

### Before Writing a Parser
- Don't guess the structure
- Evidence-based: see actual data
- Identify issues early (mixed types, wrong skiprows)

### During Debugging
- Test fails with "wrong column count"
- Use this skill to verify structure hasn't changed

### New CSV File Arrives
- Quick check before adding to pipeline
- Verify same structure as previous files

## Error Handling

### Can't Read File
**Symptom**: Permission denied or file not found
**Solution**: Verify path, check network access

### Strange Characters
**Symptom**: UnicodeDecodeError
**Solution**: Try different encodings (utf-8-sig, latin1, cp1252)

### No Header Row Found
**Symptom**: All rows look like data
**Solution**: File may have no headers, use positional indexing

## Output Files

```
projects/<name>/outputs/
└── csv-analysis-<filename>.md    # Structure report
```

---

*This skill is part of the Process Factory ANALYST toolkit.*

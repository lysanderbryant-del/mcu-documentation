---
name: analyze-excel
description: Extract and analyze Excel workbook structure (formulas, data flows, dependencies)
---

# Excel Analysis Skill

You are an Excel workbook analyst for the Process Factory framework.

## User's Request
$ARGUMENTS

## Your Task

Analyze an Excel workbook to understand its structure, formulas, data flows, and business logic.

## Step-by-Step Workflow

### 1. Locate the Excel File
Ask user: "Which Excel file should I analyze?"

Expected input:
- Path to `.xlsx`, `.xlsm`, or `.xls` file
- Or: User uploads file and you note the path

### 2. Create Project Analysis Directory
```bash
PROJECT_DIR=projects/<project-name>
mkdir -p $PROJECT_DIR/requests/excel_extracted
```

### 3. Extract Excel Structure
Excel files are ZIP archives. Extract them:

```bash
# Copy file to requests/
cp /path/to/file.xlsx $PROJECT_DIR/requests/

# Extract (Excel = ZIP format)
cd $PROJECT_DIR/requests
unzip -q "filename.xlsx" -d excel_extracted/

# Key locations after extraction:
# - xl/worksheets/ → Sheet XML files
# - xl/sharedStrings.xml → All text values
# - xl/calcChain.xml → Formula calculation order
# - xl/workbook.xml → Sheet names and structure
```

### 4. Analyze Workbook Structure
Read these files to understand structure:

**Sheet Names** (`xl/workbook.xml`):
```xml
<sheet name="LwgSummary" sheetId="1" r:id="rId1"/>
<sheet name="Data" sheetId="2" r:id="rId2"/>
```

**Sheet Content** (`xl/worksheets/sheet1.xml`):
- Find `<row r="...">` for row numbers
- Find `<c r="A1" t="s">` for cells (r=reference, t=type)
- `t="s"` means string (lookup in sharedStrings.xml)
- `t="n"` means number (value in `<v>` tag)
- `<f>` tags contain formulas

**Example Cell with Formula**:
```xml
<c r="K82" s="2">
    <f>SUM(K10:K20)</f>
    <v>42.5</v>
</c>
```

### 5. Document Findings
Create: `$PROJECT_DIR/outputs/excel-structure-analysis.md`

**Template**:
```markdown
# Excel Structure Analysis: [Workbook Name]

**Source**: `filename.xlsx`
**Analysis Date**: YYYY-MM-DD
**Project**: [project-name]

---

## Workbook Overview
- **Sheets**: [List all sheet names]
- **Purpose**: [What this workbook does]
- **Key Calculations**: [Main outputs]

---

## Sheet: [Sheet Name]

### Layout
| Column | Header | Purpose | Formula Pattern |
|--------|--------|---------|-----------------|
| A | Date | Business date | Manual entry |
| B | Amount | Position value | =SUM(...) |
| C | FX Rate | EUR/GBP | =VLOOKUP(...) |

### Key Formulas

**Cell K82** - Total BNP Margin:
```excel
=SUM(K10:K50) + K55 - K60
```
- K10:K50 = Individual product positions
- K55 = Spot/Physical delivery
- K60 = Cascading adjustments

**Cell L82** - Movement Analysis:
```excel
=K82 - P82
```
- Compares today (K) vs prior date (P)

### Data Hierarchy
```
Level 1: Granular Products (rows 10-50)
├── Product A: K10 = 10.5M
├── Product B: K15 = 5.2M
└── ...

Level 2: Category Totals (rows 55-60)
├── Total Open: K55 = SUM(Level 1)
├── Physical: K56 = [from another sheet]
└── Cascading: K57 = [adjustment]

Level 3: Grand Total (row 82)
└── BNP CEL Total: K82 = SUM(Level 2)
```

### External References
- **Sheet 'Data'!A:B** - Source data for product positions
- **Sheet 'FX Rates'!C:D** - Currency conversion rates
- **File 'PriorDay.xlsx'!Summary** - Prior date comparison

### Calculation Dependencies
```
[Raw Data] → [Product Calc] → [Category Sum] → [Grand Total]
     ↓              ↓               ↓              ↓
  Sheet2         K10:K50         K55:K60         K82
```

---

## Business Logic Extracted

### Calculation 1: Total Margin
**Formula**: `=SUM(Exchange_Margin) + Physical_Delivery - Cascading_Adjustments`
**Purpose**: Daily margin reconciliation total
**Target**: £65.11M (for reference date)

### Calculation 2: Movement Analysis
**Formula**: `=Today_Value - Prior_Date_Value`
**Purpose**: Explain day-over-day variance
**Users**: Treasury team needs to explain £X change

### Calculation 3: FX Conversion
**Formula**: `=EUR_Amount * VLOOKUP(Date, FX_Rates, 2)`
**Purpose**: Convert EUR positions to GBP reporting
**Rate Source**: [ECB, manual entry, etc.]

---

## Data Sources Identified

1. **CSV File**: `Detailed_Open_Pos_*.csv`
   - Contains: Product-level OTE values
   - Feeds: Cells K10:K50

2. **CSV File**: `Journal_Entries_*.csv`
   - Contains: Spot/Physical transactions
   - Feeds: Cell K56

3. **Manual Entry**: FX rates
   - Update frequency: Daily
   - Location: Sheet 'FX Rates'

---

## Automation Opportunities

### Replace with Automated Solution:
- ✓ CSV parsing (currently manual copy/paste)
- ✓ Formula calculations (implement in Python/SQL)
- ✓ Movement analysis (database query instead)

### Keep Manual:
- FX rate entry (needs approval)
- Commentary/notes

### Benefits:
- Time saved: 2 hours/day → 5 minutes
- Error reduction: No copy/paste mistakes
- Audit trail: Database logs all changes

---

## Recommended Implementation

**Database Schema**:
```sql
CREATE TABLE positions (
    date DATE,
    product TEXT,
    currency TEXT,
    value REAL
)
```

**Calculation Logic** (Python):
```python
total = sum(row['value'] for row in positions 
            where row['date'] == today)
movement = total - prior_total
```

**Replacement**: Web app with same layout as Excel

---

## Next Steps

1. ✓ Extract all formulas from sheets
2. [ ] Map CSV sources to Excel inputs
3. [ ] Design database schema
4. [ ] Write tests for calculations (TDD)
5. [ ] Build automated replacement

---

*Analysis complete. Ready for ARCHITECT phase.*
```

### 6. Create Visual Diagram (Optional)
If complex data flows exist, create:
`$PROJECT_DIR/outputs/excel-data-flow.md`

Use ASCII art or describe flow:
```
CSV Files → Excel Import → Formulas → Summary Tab → Report
    ↓           ↓            ↓           ↓
  BNP.csv    Sheet2       K82       LwgSummary
```

### 7. Summarize for User
Report findings:
- Number of sheets analyzed
- Key calculations identified
- Data sources discovered
- Automation opportunities found

Ask: "Would you like me to proceed to ARCHITECT phase to design the replacement?"

---

## Key Analysis Patterns

### Pattern 1: Waterfall/Cascade Structure
Excel shows: Row 10 + Row 15 + Row 20 = Row 82
Means: Hierarchical aggregation (products → categories → total)

### Pattern 2: Comparison Columns
Excel shows: Column K (today) vs Column P (prior)
Means: Movement analysis is core requirement

### Pattern 3: VLOOKUP / External References
Excel shows: `=VLOOKUP(A1, OtherSheet!A:B, 2)`
Means: Data integration from multiple sources

### Pattern 4: Named Ranges
Excel shows: `=SUM(ProductRange)`
Means: Abstracted cell references (safer formulas)

### Pattern 5: Circular Dependencies
Excel shows: Warning messages or `[Circular]`
Means: Iterative calculations (handle with care)

---

## Tools You Can Use

### 1. Unzip Excel File
```bash
unzip -q file.xlsx -d extracted/
```

### 2. Find All Formulas
```bash
grep -r "<f>" extracted/xl/worksheets/ | head -50
```

### 3. List All Sheets
```bash
cat extracted/xl/workbook.xml | grep -o 'name="[^"]*"'
```

### 4. Extract Shared Strings (Text Values)
```bash
cat extracted/xl/sharedStrings.xml | grep "<t>" | sed 's/<[^>]*>//g'
```

### 5. Find Calculation Chain
```bash
cat extracted/xl/calcChain.xml  # Shows formula calc order
```

---

## Common Issues

### Issue 1: Password-Protected Sheets
**Symptom**: Cannot extract with unzip
**Solution**: Ask user to remove protection first

### Issue 2: Binary Format (.xls)
**Symptom**: Extraction fails (not ZIP format)
**Solution**: Ask user to convert to .xlsx first

### Issue 3: Macros (VBA Code)
**Location**: `xl/vbaProject.bin` (binary, hard to read)
**Solution**: Ask user to export VBA code to text, or note "contains macros, needs manual review"

### Issue 4: External Links
**Symptom**: Formulas reference `[OtherFile.xlsx]Sheet1!A1`
**Solution**: Document external dependencies, ask for those files too

---

## Output Files

After analysis, project should have:

```
projects/<name>/
├── requests/
│   ├── original_file.xlsx           # Original Excel
│   ├── latest.json                  # Context about request
│   └── excel_extracted/             # Extracted XML
│       ├── xl/worksheets/
│       ├── xl/sharedStrings.xml
│       └── xl/workbook.xml
└── outputs/
    ├── excel-structure-analysis.md  # Main analysis
    └── excel-data-flow.md           # Visual diagram (optional)
```

---

## Remember

1. **Evidence-based**: Read actual XML, don't guess
2. **Focus on business logic**: Why does this formula exist?
3. **Identify automation opportunities**: What's manual that shouldn't be?
4. **Document clearly**: Next person should understand without Excel open
5. **Prepare for next phase**: Your analysis feeds ARCHITECT

---

*This skill is part of the Process Factory framework.*
*It typically runs in the ANALYST phase before ARCHITECT/TESTER/BUILDER.*

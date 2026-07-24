# Excel Analysis Skills

Two reusable skills for analyzing Excel workbooks as part of Process Factory projects.

## Skills Overview

| Skill | Command | Purpose | Phase |
|-------|---------|---------|-------|
| **extract-excel** | `/extract-excel path/to/file.xlsx` | Quick extraction of Excel XML structure | ANALYST |
| **analyze-excel** | `/analyze-excel` | Full analysis of formulas, data flows, business logic | ANALYST |

## Workflow

### 1. Extract Excel Structure
```bash
/extract-excel C:\Reports\MarginSummary.xlsx
```

**What happens**:
- Copies Excel file to `projects/<name>/requests/`
- Extracts XML (Excel = ZIP format)
- Shows quick stats (sheets, formulas, size)
- Verifies extraction successful

**Output**:
```
projects/<name>/requests/
├── MarginSummary.xlsx
└── excel_extracted/
    └── xl/
        ├── workbook.xml         # Sheet list
        ├── sharedStrings.xml    # Text values
        ├── worksheets/
        │   ├── sheet1.xml       # Sheet data
        │   └── sheet2.xml
        └── calcChain.xml        # Formula calc order
```

### 2. Analyze Structure
```bash
/analyze-excel
```

**What happens**:
- Reads extracted XML files
- Maps sheet structure (columns, headers, layout)
- Extracts all formulas with explanations
- Identifies data hierarchy (products → categories → totals)
- Documents external references (other sheets, files)
- Finds data sources (CSV imports, manual entry)
- Recommends automation approach

**Output**: `projects/<name>/outputs/excel-structure-analysis.md`

Example content:
```markdown
# Excel Structure Analysis: MarginSummary.xlsx

## Sheet: LwgSummary

### Key Formulas

**Cell K82** - Total BNP Margin:
```excel
=SUM(K10:K50) + K55 - K60
```

### Data Hierarchy
Level 1: Products (K10:K50)
Level 2: Categories (K55:K60)
Level 3: Grand Total (K82)

### Data Sources
- CSV: Detailed_Open_Pos_*.csv → K10:K50
- CSV: Journal_Entries_*.csv → K55
- Manual: FX rates → Sheet 'FX Rates'

### Automation Opportunity
Replace with: Database + Python script
Time saved: 2 hours/day → 5 minutes
```

## What Gets Extracted

### Structure Analysis
- Sheet names and purposes
- Column layout (headers, data types)
- Row ranges (data vs calculations)
- Named ranges

### Formula Analysis
- All formula cells with locations
- Calculation dependencies (A depends on B)
- External references (other sheets/files)
- Aggregation patterns (SUM, VLOOKUP, etc.)

### Data Flow Analysis
```
[CSV Files] → [Import Tab] → [Calculations] → [Summary Tab]
     ↓             ↓              ↓               ↓
  Source        Raw Data      Business        Output
                              Logic
```

### Business Logic
- What the workbook calculates (margin, P&L, forecast)
- Why (reconciliation, reporting, decision support)
- How (sum of products, movement analysis, FX conversion)
- Target values (£65.11M, tolerance ±£0.01M)

## Learning from MCU Example

### What We Discovered
**Excel File**: `CeMarginMoveSummary_20260722.xlsm` (18MB)

**Structure**:
- **Sheet 'LwgSummary'**: 111 rows, 19 columns
- **Key Range**: L48:S158 (comparison layout)
- **Formula Pattern**: Column K (today) vs Column P (prior date)

**Hierarchy**:
1. **Level 1** (rows 82-101): 20 granular products
   - EEX TTF Natural Gas Month Futures: €0.057M
   - ICE TTF Natural Gas Futures: €47.845M
   - NBP Natural Gas: £12.158M
2. **Level 2** (rows 102-110): 9 category totals
   - Total BNP Open movement: €29.455M
   - Spot/Physical Delivery: €23.509M
3. **Level 3** (row 82): Grand total
   - BNP CEL Margin call: €52.656M

**Formulas Extracted**:
```excel
K82 = SUM(K10:K50) + K55 + K56 - K57
```

**Data Sources Identified**:
- `Detailed_Open_Pos_*.csv` → Product positions (K10:K50)
- `Journal_Entries_*.csv` → Physical delivery (K55)
- `PnS_*.csv` → Cascading adjustments (K57)

**Automation Designed**:
- Replace manual Excel with 7 CSV parsers
- Load to SQLite database
- Automated reconciliation (target: £65.11M)
- TDD approach (14 tests written)

## When to Use These Skills

### Use `/extract-excel` when:
- Starting a new project with Excel workbook
- Need quick view of structure
- Want to count formulas/sheets
- Preparing for full analysis

### Use `/analyze-excel` when:
- Need to understand business logic
- Designing automated replacement
- Documenting current process
- Extracting requirements for TDD

### Use both together:
1. `/extract-excel` → Quick verification
2. `/analyze-excel` → Deep analysis
3. `/factory` → Design → Test → Build replacement

## Common Patterns Identified

### Pattern 1: Manual Reconciliation
**Excel**: Copy/paste CSV data, run formulas, compare totals
**Replacement**: Automated parsers → database → validation

### Pattern 2: Multi-Source Aggregation
**Excel**: VLOOKUP across 5 sheets from different systems
**Replacement**: Database joins, single source of truth

### Pattern 3: Movement Analysis
**Excel**: Column A (today) vs Column B (yesterday), manual variance
**Replacement**: SQL query comparing two dates

### Pattern 4: Hierarchical Summaries
**Excel**: Product level → Category → Total (nested SUM formulas)
**Replacement**: Database schema with `level` and `parent_category` columns

### Pattern 5: FX Conversion
**Excel**: Manual FX rate entry, multiply by position
**Replacement**: API fetch + automated conversion

## Example: Analyzing Invoice Approval Workbook

```bash
# 1. Extract
/extract-excel C:\Finance\InvoiceApproval.xlsx

# Output:
# ✓ 3 sheets found: Pending, Approved, Rejected
# ✓ 127 formulas
# ✓ 1,234 rows of data

# 2. Analyze
/analyze-excel

# Creates: projects/invoice-optimizer/outputs/excel-structure-analysis.md
# Contains:
# - Approval workflow logic
# - Budget vs actual formulas
# - Data validation rules
# - External reference to GL system
# - Automation opportunity: Replace with web app
```

## Benefits

### Time Saved
- Manual Excel analysis: 4-6 hours
- Automated skill: 5-10 minutes

### Consistency
- Every project follows same analysis pattern
- Standard output format
- Nothing missed (all formulas extracted)

### Documentation
- Clear evidence trail in `outputs/`
- Next phase (ARCHITECT) has full requirements
- Team can review without Excel open

### Reusability
- Learn once (MCU)
- Apply everywhere (invoices, reports, forecasts)
- Framework gets smarter with each project

## Next Steps After Analysis

1. **Review Analysis**: Check `outputs/excel-structure-analysis.md`
2. **Clarify Questions**: Ask user about unclear formulas
3. **Run `/factory`**: Proceed to ARCHITECT → TESTER → BUILDER
4. **Design Replacement**: Database schema, parser logic, UI
5. **Write Tests**: TDD approach (RED → GREEN → REFACTOR)
6. **Build Solution**: Automated system replacing Excel

## See Also

- [Process Factory README](../README.md)
- [MCU Excel Analysis](../projects/mcu/outputs/excel-structure-analysis.md)
- [Conductor UI Setup](conductor-ui-setup.md)
- [STRUCTURE.md](../STRUCTURE.md)

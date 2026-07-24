---
name: extract-excel
description: Quick extraction of Excel workbook to XML for analysis
---

# Excel Extraction Skill

Quick command to extract an Excel workbook's internal XML structure.

## Usage

User says: `/extract-excel path/to/file.xlsx`

## What You Do

### 1. Determine Project Context
```bash
# If in MCU project
PROJECT_DIR=projects/mcu

# If starting new project
PROJECT_DIR=projects/<project-name>
mkdir -p $PROJECT_DIR/requests
```

### 2. Copy Excel File to Requests
```bash
cp "$USER_PROVIDED_PATH" $PROJECT_DIR/requests/
cd $PROJECT_DIR/requests
```

### 3. Extract Excel Structure
```bash
# Excel files (.xlsx, .xlsm) are ZIP archives
FILENAME=$(basename "$USER_PROVIDED_PATH")
unzip -q "$FILENAME" -d excel_extracted/

echo "✓ Extracted to: $PROJECT_DIR/requests/excel_extracted/"
```

### 4. Quick Verification
```bash
# List sheets
echo "=== Sheets Found ==="
cat excel_extracted/xl/workbook.xml | grep -o 'name="[^"]*"'

# Count formulas
echo "=== Formula Count ==="
find excel_extracted/xl/worksheets/ -name "*.xml" -exec grep -c "<f>" {} \; | awk '{s+=$1} END {print s " formulas found"}'

# Show first 10 formulas
echo "=== Sample Formulas ==="
grep -rh "<f>" excel_extracted/xl/worksheets/ | sed 's/.*<f>\(.*\)<\/f>.*/\1/' | head -10
```

### 5. Report to User
```
✓ Extraction complete

**File**: filename.xlsx
**Location**: projects/<name>/requests/excel_extracted/

**Quick Stats**:
- Sheets: [count]
- Formulas: [count]
- Size: [KB]

**Key Locations**:
- Sheet XML: `xl/worksheets/sheet1.xml`, `sheet2.xml`, ...
- Text values: `xl/sharedStrings.xml`
- Structure: `xl/workbook.xml`

**Next**: Run `/analyze-excel` for full structural analysis
```

---

## File Structure After Extraction

```
projects/<name>/requests/
├── filename.xlsx                    # Original file
└── excel_extracted/                 # Extracted contents
    ├── [Content_Types].xml          # File manifest
    ├── _rels/                       # Relationships
    ├── xl/
    │   ├── workbook.xml             # Sheet list & structure
    │   ├── sharedStrings.xml        # All text values
    │   ├── styles.xml               # Cell formatting
    │   ├── calcChain.xml            # Formula calc order
    │   ├── worksheets/
    │   │   ├── sheet1.xml           # Sheet 1 data
    │   │   ├── sheet2.xml           # Sheet 2 data
    │   │   └── ...
    │   ├── charts/                  # Embedded charts
    │   └── drawings/                # Embedded images
    ├── docProps/                    # Metadata (author, date)
    └── customXml/                   # Custom XML data
```

---

## Quick Reference Commands

### List All Sheets
```bash
cat excel_extracted/xl/workbook.xml | grep -o 'name="[^"]*"' | sed 's/name="//;s/"//'
```

### Find All Formulas in Sheet 1
```bash
grep "<f>" excel_extracted/xl/worksheets/sheet1.xml
```

### Extract Cell A1 Value
```bash
# Find cell A1
grep 'r="A1"' excel_extracted/xl/worksheets/sheet1.xml
# If t="s", lookup index in sharedStrings.xml
# If t="n", value is in <v> tag
```

### Count Total Cells with Data
```bash
grep -c "<c r=" excel_extracted/xl/worksheets/sheet1.xml
```

---

## Error Handling

### Error: "Archive format not recognized"
**Cause**: File is `.xls` (binary format, not ZIP)
**Fix**: Ask user to convert to `.xlsx` in Excel first

### Error: "Password required"
**Cause**: Workbook is encrypted
**Fix**: Ask user to remove password protection

### Error: "File not found"
**Cause**: Wrong path or permission issue
**Fix**: Verify file exists and is readable

---

## Example Session

```
User: /extract-excel C:\Reports\MarginSummary.xlsx
# Find Latest File Skill

**Agent**: ANALYST  
**Purpose**: Find the most recent file matching a date-based pattern with wildcard timestamps

---

## When to Use

- CSV files with timestamps: `Report_2026_07_24_074005.csv`
- Date folders with varying run times: `2026-Jul\Statement_20260724_163022.csv`
- Need to find "today's file" without knowing exact timestamp
- Writing tests that should work across multiple dates
- File discovery for daily automated processes

**Don't use for**:
- Exact known file paths (just use Path directly)
- Files without date patterns (use simple glob)
- When you need ALL files, not just latest (use glob + sorted)

---

## The Pattern

Many data sources append timestamps to filenames:
```
Collateral_Summary_2026_07_24_074005.csv
Collateral_Summary_2026_07_24_163022.csv  ← Different run time
Collateral_Summary_2026_07_25_074003.csv  ← Next day
```

Tests/code should find latest for a given date without hardcoding timestamp.

---

## Quick Reference

**In test code**:
```python
from pathlib import Path
import pytest

def _find_latest_file(base_dir: Path, business_date, pattern_template: str) -> Path:
    """
    Find most recent file matching date pattern.
    
    Args:
        base_dir: Directory to search
        business_date: date object
        pattern_template: e.g., 'Report_{date}_*.csv' (use {date} placeholder)
    
    Returns:
        Path to latest file
    
    Raises:
        pytest.skip: If directory/files not found
    """
    if not base_dir.exists():
        pytest.skip(f"Share not accessible: {base_dir}")
    
    # Format date into pattern
    date_str = business_date.strftime('%Y_%m_%d')  # Adjust format as needed
    pattern = pattern_template.replace('{date}', date_str)
    
    matches = list(base_dir.glob(pattern))
    
    if not matches:
        pytest.skip(f"No files found: {pattern}")
    
    # Return most recent by modification time
    return max(matches, key=lambda p: p.stat().st_mtime)
```

**Usage**:
```python
TEST_DATE = date(2026, 7, 24)
TEST_FILE = _find_latest_file(
    Path(r'\\server\share\folder'),
    TEST_DATE,
    'Report_{date}_*.csv'
)
```

---

## Step-by-Step Workflow

### 1. Identify File Pattern

Look at actual filenames in directory:
```
Collateral_Summary_2026_07_22_074004.csv
Collateral_Summary_2026_07_23_080512.csv
Collateral_Summary_2026_07_24_074005.csv
```

**Pattern**: `Collateral_Summary_{YYYY_MM_DD}_{HHMMSS}.csv`

**Fixed parts**: `Collateral_Summary_`, `.csv`  
**Date part**: `2026_07_24` (varies by business date)  
**Wildcard part**: `074005` (timestamp - don't care)

### 2. Determine Date Format

Common formats:
- `YYYY_MM_DD` → `2026_07_24` → Use `strftime('%Y_%m_%d')`
- `YYYY-MM-DD` → `2026-07-24` → Use `strftime('%Y-%m-%d')`
- `YYYYMMDD` → `20260724` → Use `strftime('%Y%m%d')`
- `DDMMYYYY` → `24072026` → Use `strftime('%d%m%Y')`

### 3. Build Glob Pattern

Replace variable parts with wildcards:
```python
# Fixed: Collateral_Summary_
# Date:  2026_07_24
# Wild:  *
# Fixed: .csv

pattern = f'Collateral_Summary_{date_str}_*.csv'
```

### 4. Search and Select Latest

```python
matches = list(base_dir.glob(pattern))

if not matches:
    pytest.skip(f"No files found: {pattern}")

# Sort by modification time, take newest
latest_file = max(matches, key=lambda p: p.stat().st_mtime)
```

**Alternative sorts**:
- By name (alphabetical): `max(matches, key=lambda p: p.name)`
- By size: `max(matches, key=lambda p: p.stat().st_size)`
- By creation time: `max(matches, key=lambda p: p.stat().st_ctime)`

### 5. Handle Errors

**Directory doesn't exist** (network share unmounted):
```python
if not base_dir.exists():
    pytest.skip(f"Share not accessible: {base_dir}")
```

**No files match** (wrong date, files not generated yet):
```python
if not matches:
    pytest.skip(f"No files for {business_date}")
```

**Use pytest.skip()** not raise - allows tests to pass gracefully when files unavailable.

---

## Complete Example (MCU CSA)

### Before (Hardcoded Timestamp)
```python
class TestCSACollateralParser:
    TEST_FILE = Path('\\\\server\\share\\Collateral_Summary_2026_07_22_074004.csv')
    TEST_DATE = date(2026, 7, 22)
    
    def test_parser(self):
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)
        # FAILS: File from July 22 doesn't exist on July 24
```

### After (Dynamic Discovery)
```python
class TestCSACollateralParser:
    CSA_BASE = Path(r'\\server\share')
    TEST_DATE = date(2026, 7, 24)  # Today
    
    @classmethod
    def _find_latest_csa_file(cls) -> Path:
        """Find most recent CSA file for TEST_DATE."""
        pattern = f'Collateral_Summary_{cls.TEST_DATE.strftime("%Y_%m_%d")}_*.csv'
        
        if not cls.CSA_BASE.exists():
            pytest.skip(f"CSA share not accessible: {cls.CSA_BASE}")
        
        matches = list(cls.CSA_BASE.glob(pattern))
        
        if not matches:
            pytest.skip(f"No CSA file for {cls.TEST_DATE}")
        
        return max(matches, key=lambda p: p.stat().st_mtime)
    
    @property
    def TEST_FILE(self):
        """Dynamically find latest test file."""
        return self._find_latest_csa_file()
    
    def test_parser(self):
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)
        # PASSES: Always uses latest file for TEST_DATE
```

**Benefits**:
- ✓ Tests work across multiple days
- ✓ Don't need to update hardcoded timestamps
- ✓ Gracefully skips when share unavailable
- ✓ Always tests against "today's" data

---

## Advanced: Multiple Date Formats in One Directory

Some directories have multiple formats:
```
Report_2026-07-24_163022.csv     ← ISO date
Report_20260724_163022.csv       ← Compact date
Report_24072026_163022.csv       ← UK date
```

Try each format until match found:
```python
def _find_latest_file_multi_format(base_dir, business_date, formats):
    """
    Try multiple date formats.
    
    Args:
        formats: List of (strftime_format, pattern_template) tuples
    """
    if not base_dir.exists():
        pytest.skip(f"Directory not accessible: {base_dir}")
    
    for fmt, template in formats:
        date_str = business_date.strftime(fmt)
        pattern = template.replace('{date}', date_str)
        matches = list(base_dir.glob(pattern))
        
        if matches:
            return max(matches, key=lambda p: p.stat().st_mtime)
    
    pytest.skip(f"No files found for {business_date} (tried {len(formats)} formats)")

# Usage
TEST_FILE = _find_latest_file_multi_format(
    base_dir,
    date(2026, 7, 24),
    [
        ('%Y-%m-%d', 'Report_{date}_*.csv'),   # Try ISO first
        ('%Y%m%d', 'Report_{date}_*.csv'),     # Then compact
        ('%d%m%Y', 'Report_{date}_*.csv'),     # Then UK
    ]
)
```

---

## Integration with File Discovery Module

If `src/loaders/file_discovery.py` exists, use its logic:
```python
from src.loaders.file_discovery import DailyFileDiscovery

def _find_latest_file_via_discovery(file_type: str, business_date: date) -> Path:
    """Use existing file discovery module."""
    discovery = DailyFileDiscovery(business_date)
    
    try:
        files = discovery.discover_all_files()
        source_file = files[file_type]
        
        if not source_file.exists:
            pytest.skip(f"{file_type} not found for {business_date}")
        
        return source_file.file_path
    
    except Exception as e:
        pytest.skip(f"File discovery failed: {e}")

# Usage
TEST_FILE = _find_latest_file_via_discovery('csa', date(2026, 7, 24))
```

**Benefits**:
- Reuses production file discovery logic
- Tests and production use same search algorithm
- If file location changes, update in one place

---

## Common Patterns by Source

### BNP Files (Date in filename + subfolder)
```python
base = Path(r'\\server\ENDUR_PROD_01\Interface\BNPFileStore\Processed')
month_folder = business_date.strftime('%Y-%b')  # 2026-Jul
directory = base / month_folder

pattern = f'MC_Statement_CEL U_{business_date.strftime("%Y-%m-%d")}_*.csv'
latest = max(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
```

### SocGen (Exact filename, no wildcard)
```python
base = Path(r'\\server\SGSAFileStore\SocGenAAL')
filename = f'{business_date.strftime("%Y%m%d")}_GlobalMarginUnderlyingCurrencyReport.csv'
file_path = base / filename

if not file_path.exists():
    pytest.skip(f"SocGen file not found: {filename}")
```

### CSA (Date with underscore + wildcard timestamp)
```python
base = Path(r'\\server\CreditRisk\Collateral')
pattern = f'Collateral_Summary_{business_date.strftime("%Y_%m_%d")}_*.csv'
latest = max(base.glob(pattern), key=lambda p: p.stat().st_mtime)
```

---

## Testing the Skill

Verify file discovery logic works:
```python
def test_find_latest_file_logic():
    """Test file discovery on known directory."""
    from datetime import date
    from pathlib import Path
    
    base = Path(r'\\test\share')
    test_date = date(2026, 7, 24)
    
    # Find file
    pattern = f'Report_{test_date.strftime("%Y_%m_%d")}_*.csv'
    matches = list(base.glob(pattern))
    
    assert len(matches) > 0, f"No files found: {pattern}"
    
    latest = max(matches, key=lambda p: p.stat().st_mtime)
    print(f"Found: {latest.name}")
    print(f"Size: {latest.stat().st_size} bytes")
    print(f"Modified: {latest.stat().st_mtime}")
```

---

## Summary

**Problem**: Files have unpredictable timestamps  
**Solution**: Glob pattern with date + wildcard, select latest by mtime  
**Agent**: ANALYST (file discovery is evidence gathering)  
**Key**: Use `strftime()` to format date, `glob()` with `*` for timestamp, `max()` by `st_mtime`

**Pattern**:
```python
pattern = f'Filename_{date.strftime("%Y_%m_%d")}_*.csv'
matches = list(base_dir.glob(pattern))
latest = max(matches, key=lambda p: p.stat().st_mtime)
```

---

*Skill created from MCU CSA file discovery issue (2026-07-24)*

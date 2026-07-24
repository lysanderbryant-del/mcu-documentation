# Troubleshoot Network File Access

**Agent**: ANALYST  
**Purpose**: Diagnose and resolve network share access issues in tests/code

---

## When to Use

**Symptoms**:
- `FileNotFoundError` for network UNC paths (`\\server\share\...`)
- Tests failing with "The system cannot find the file specified"
- User says "I can access it" but Claude Code cannot
- `Path.exists()` returns `False` for network paths

**Common scenarios**:
- Tests need CSV files from network shares
- Production code reads from `\\server\share\...` paths
- File discovery for daily automated processes

---

## Root Cause

**Claude Code's bash environment runs as your user account** but:
- Cannot interactively browse network shares
- Cannot mount shares with `net use`
- **CAN** run Python which inherits your Windows credentials

**Solution**: Use Python (with your credentials) instead of bash for network operations.

---

## Diagnostic Steps

### Step 1: Verify Network Connectivity

```bash
# Test if server is reachable
ping app-nas-fsx-prod.uk.centricaplc.com
```

**Expected**: Reply from IP address  
**If fails**: VPN/network issue (not credentials)

### Step 2: Test Path from Bash (Will Fail)

```bash
# This will return False even if you have access
python -c "from pathlib import Path; print(Path(r'\\server\share').exists())"
```

**Expected**: `False` (bash can't see share)  
**Reason**: Bash shell doesn't inherit Windows credentials

### Step 3: Test via User's Python (Should Work)

```bash
# Run test that uses the file - this WILL work
cd project_dir
python -m pytest tests/test_parser.py -v
```

**Expected**: Tests run and access file successfully  
**Reason**: Python runs as your Windows user, inherits credentials

---

## Solution Pattern

### ✗ Don't Do This (Fails)

```python
# In Claude Code bash
from pathlib import Path
file = Path(r'\\server\share\file.csv')
if file.exists():  # Always False in bash
    ...
```

### ✓ Do This Instead (Works)

**Option A: Run tests directly** (they use your credentials):
```bash
python -m pytest tests/test_with_network_files.py -v
```

**Option B: Use pytest.skip() for graceful handling**:
```python
# In test file
TEST_FILE = Path(r'\\server\share\file.csv')

def test_parser(self):
    if not TEST_FILE.exists():
        pytest.skip(f"Network file not accessible: {TEST_FILE}")
    
    # Test continues if file accessible
    result = parser.parse(TEST_FILE)
    assert result is not None
```

**Option C: Use dynamic file discovery** (with skip):
```python
@classmethod
def _find_file(cls):
    base = Path(r'\\server\share\folder')
    
    if not base.exists():
        pytest.skip(f"Network share not accessible: {base}")
    
    matches = list(base.glob('file_*.csv'))
    if not matches:
        pytest.skip(f"No files found in {base}")
    
    return max(matches, key=lambda p: p.stat().st_mtime)
```

---

## Common Issues & Fixes

### Issue 1: Hardcoded Timestamps

**Problem**:
```python
TEST_FILE = Path('\\\\server\\share\\Report_2026_07_22_074004.csv')
# File from July 22 doesn't exist on July 24
```

**Fix**: Use wildcard discovery (see `/find-latest-file` skill)
```python
pattern = f'Report_{date.strftime("%Y_%m_%d")}_*.csv'
matches = list(base_dir.glob(pattern))
TEST_FILE = max(matches, key=lambda p: p.stat().st_mtime)
```

### Issue 2: Wrong Server Name Format

**Problem**:
```python
# Using FQDN
Path('\\\\app-nas-fsx-prod.uk.centricaplc.com\\share')

# Using short name
Path('\\\\app-nas-fsx-prod\\share')
```

**Fix**: Try both formats, or check DNS:
```bash
nslookup app-nas-fsx-prod.uk.centricaplc.com
# Returns: awle-p-fsx-001.uk.centricaplc.com

# Try actual hostname
Path('\\\\awle-p-fsx-001\\share')
```

**Note**: User confirmation is best - "What path works for you?"

### Issue 3: Path Format (Forward vs Back Slashes)

**Problem**:
```python
# Unix style (may not work)
Path('//server/share/file.csv')

# Windows style (correct)
Path('\\\\server\\share\\file.csv')
```

**Fix**: Use raw string with backslashes:
```python
Path(r'\\server\share\file.csv')
```

**Python Path handles both**, but tests may hardcode format.

### Issue 4: Not Using User's Credentials

**Problem**: Trying to access from bash directly
```bash
# This can't use Windows credentials
dir "\\\\server\\share"  # Fails in bash
```

**Fix**: Run via Python (inherits credentials)
```bash
python -c "from pathlib import Path; print(list(Path(r'\\server\share').iterdir()))"
```

---

## Verification Checklist

When user says "I can access it":

1. **Ask for exact path** user uses:
   ```
   User: "I can access \\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01"
   ```

2. **Check if files have variable timestamps**:
   ```
   "Does the filename have numbers after the date?"
   User: "Yes, like Collateral_Summary_2026_07_24_074005.csv"
   → Use /find-latest-file skill
   ```

3. **Test via pytest** (not bash):
   ```bash
   python -m pytest tests/test_file.py::test_network_file -v
   ```

4. **If test passes** → File accessible, bash browsing just doesn't work
   **If test fails** → Real access issue (permissions, VPN, wrong path)

---

## Implementation Pattern

### Test Setup with Network Files

```python
import pytest
from pathlib import Path
from datetime import date

class TestNetworkParser:
    """Test parser that reads from network share."""
    
    # Network share base path
    SHARE_BASE = Path(r'\\server\share\folder')
    TEST_DATE = date(2026, 7, 24)
    
    @classmethod
    def _find_latest_file(cls) -> Path:
        """Find latest file for TEST_DATE with dynamic timestamp."""
        pattern = f'Report_{cls.TEST_DATE.strftime("%Y_%m_%d")}_*.csv'
        
        if not cls.SHARE_BASE.exists():
            pytest.skip(f"Network share not accessible: {cls.SHARE_BASE}")
        
        matches = list(cls.SHARE_BASE.glob(pattern))
        
        if not matches:
            pytest.skip(f"No files found: {pattern}")
        
        return max(matches, key=lambda p: p.stat().st_mtime)
    
    @property
    def TEST_FILE(self):
        """Dynamically discover test file."""
        return self._find_latest_file()
    
    def test_parser_works(self):
        """Test parser with network file."""
        from src.parser import Parser
        
        parser = Parser()
        result = parser.parse(self.TEST_FILE, self.TEST_DATE)
        
        assert result is not None
        assert len(result) > 0
```

**Key features**:
- ✓ Uses `pytest.skip()` if share unavailable (test passes, notes skipped)
- ✓ Dynamic file discovery (works across dates)
- ✓ Runs with user credentials (Python inherits)
- ✓ Clear error messages if file not found

---

## When You See This Error

```
FileNotFoundError: [WinError 2] The system cannot find the file specified:
  '\\\\app-nas-fsx-prod.uk.centricaplc.com\\...'
```

**Immediate actions**:

1. **Ask user**: "Can you access `\\app-nas-fsx-prod...` in File Explorer?"
   - **Yes** → Use pattern above (pytest.skip + dynamic discovery)
   - **No** → Real permission issue, user needs to mount share

2. **Check for hardcoded timestamps** in test:
   ```python
   # Bad: Won't work next day
   TEST_FILE = Path('...\\file_2026_07_22_074004.csv')
   
   # Good: Works any day
   TEST_FILE = _find_latest_file(...)
   ```

3. **Run test via pytest** (not bash):
   ```bash
   python -m pytest tests/test_that_fails.py -v
   ```
   
   If now passes → It's bash limitation, not real issue

4. **If still fails**, check:
   - VPN connected?
   - Correct server name? (`nslookup` to verify)
   - File actually exists for that date?

---

## Key Insight

**Claude Code bash ≠ Windows user environment**

- Bash can't see network shares (even when mounted)
- Python runs AS the Windows user (can see shares)
- Tests work, interactive browsing doesn't

**Solution**: Always run tests with `python -m pytest`, not interactive `ls/dir`

---

## Skill Dependencies

- **`/find-latest-file`**: Dynamic file discovery with wildcards
- **`/compare-actual-vs-target`**: Verify files loaded correctly

---

## Future Enhancement

**Could we create a helper function?**

```python
# utils/network_files.py
import pytest
from pathlib import Path

def require_network_file(path: Path) -> Path:
    """
    Check network file exists, skip test if not.
    
    Args:
        path: Network UNC path
    
    Returns:
        Same path (for chaining)
    
    Raises:
        pytest.skip: If file not accessible
    """
    if not path.exists():
        pytest.skip(f"Network file not accessible: {path}")
    return path

# Usage in tests
TEST_FILE = require_network_file(Path(r'\\server\share\file.csv'))
```

---

## Summary

**Problem**: Bash can't see network shares even with user credentials  
**Root Cause**: Claude Code bash environment ≠ Windows user environment  
**Solution**: Run tests with `python -m pytest` (uses user credentials)  
**Best Practice**: Use `pytest.skip()` + dynamic file discovery  
**Agent**: ANALYST (troubleshooting is evidence gathering)

---

*Skill created from CSA file access investigation (2026-07-24)*

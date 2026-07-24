# CSA File Access Investigation

**Date**: 2026-07-24  
**Issue**: CSA Collateral tests failing with FileNotFoundError  
**Status**: Network share accessible but file requires credentials/permissions

---

## Problem

Tests for CSA Collateral parser failing:
```
FileNotFoundError: [Errno 2] No such file or directory: 
  '//app-nas-fsx-prod.uk.centricaplc.com/CRR_PROD_01/CreditRisk/Collateral/Collateral_Summary_2026_07_22_074004.csv'
```

**Test file path** (`tests/test_remaining_parsers_tdd.py:227`):
```python
TEST_FILE = Path('//app-nas-fsx-prod.uk.centricaplc.com/CRR_PROD_01/CreditRisk/Collateral/Collateral_Summary_2026_07_22_074004.csv')
```

---

## Investigation Results

### Network Connectivity ✓
```bash
$ ping app-nas-fsx-prod.uk.centricaplc.com
Reply from 100.64.1.5: bytes=32 time=64ms TTL=57
✓ Server reachable
```

### Share Accessibility ✗
```bash
$ net use
There are no entries in the list.
✗ Share not mounted

$ dir \\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01
No such file or directory
✗ Cannot access without credentials
```

### Path Format ✓
- **Correct Windows UNC**: `\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\`
- **Test uses forward slashes**: `//app-nas...` (Python Path converts to backslashes internally)
- **Path format is fine**, issue is access permissions

---

## Root Cause

**Network share requires authentication but credentials not provided.**

Possible reasons:
1. **Not logged into Centrica domain** (if running from personal machine)
2. **Share requires explicit credentials** (not using Windows SSO)
3. **Insufficient permissions** (read access to `CRR_PROD_01` not granted)
4. **VPN required** (if working remotely)

---

## Evidence from Codebase

File discovery code (`src/loaders/file_discovery.py:33`):
```python
CSA_BASE = Path(r'\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral')
```

Excel source (`requests/excel_extracted/xl/worksheets/_rels/sheet16.xml.rels`):
```xml
Target="file:///\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\Collateral_Summary_YYYY_MM_DD_HHMMSS.csv"
```

✓ **Path confirmed from original Excel workbook** - this is the correct location.

---

## Solutions

### Option 1: Manual Network Share Mount (Recommended)

**Windows GUI Method**:
1. Open File Explorer
2. Type in address bar: `\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01`
3. Enter credentials when prompted:
   - Username: `CENTRICA\bryantl4` (or AD username)
   - Password: [domain password]
4. Check "Remember credentials"
5. Navigate to `CreditRisk\Collateral\` to verify access

**Command Line Method**:
```cmd
net use Z: \\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01 /user:CENTRICA\bryantl4 [password]
```

Then update test:
```python
TEST_FILE = Path('Z:/CreditRisk/Collateral/Collateral_Summary_2026_07_22_074004.csv')
```

### Option 2: Use UNC Path with Explicit Credentials (Python)

```python
import subprocess

# Mount share programmatically
share = r'\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01'
username = 'CENTRICA\\bryantl4'
password = os.getenv('CENTRICA_PASSWORD')  # From environment variable

subprocess.run(['net', 'use', share, f'/user:{username}', password], check=True)

# Then access files normally
file = Path(share) / 'CreditRisk' / 'Collateral' / 'Collateral_Summary_2026_07_22_074004.csv'
```

### Option 3: Mock File for TDD (Short-term)

Create test fixture:
```python
# tests/fixtures/csa_collateral_sample.csv
Our_Entity,Trading_Counterparty,Collateral_Held,Collateral_Pledged,Reporting_Currency
Centrica Energy Limited,Counterparty A,5000000,2000000,GBP
Centrica Energy Trading A/S,Counterparty B,8000000,3280000,EUR
```

Update test to use fixture:
```python
TEST_FILE = Path(__file__).parent / 'fixtures' / 'csa_collateral_sample.csv'
```

**Trade-off**: Tests pass but don't validate against real data.

### Option 4: VPN/Domain Login (If Working Remotely)

If on non-Centrica machine:
1. Connect to Centrica VPN
2. Ensure domain authentication active
3. Retry access

---

## Recommended Approach

**Immediate** (for TDD):
- Use **Option 3** (mock file) to unblock test development
- Validate parser logic works
- All tests GREEN with fixture data

**Before Production**:
- Use **Option 1** (manual mount) to verify against real files
- Run integration test with actual CSV files
- Validate £11.72M reconciliation

**Production Deployment**:
- Use **Option 2** (programmatic credentials) with environment variables
- Never hardcode passwords in code
- Use Windows Credential Manager or Azure Key Vault

---

## Impact on MCU Reconciliation

### Current Status
- ✓ BNP CEL MC: 2/2 tests GREEN (£52.66M)
- ✓ BNP OTE: 1/4 tests GREEN (£10.60M)
- ✓ BNP Journal Entries: 4/4 tests GREEN (£23.51M)
- ✗ CSA Collateral: 0/5 tests (£11.72M) **← BLOCKED BY FILE ACCESS**
- ✓ SocGen: 1/1 tests GREEN (-£11.12M)

### Reconciliation Impact
- **Can achieve**: £65.11M - £11.72M = £53.39M (82% of target)
- **Blocked**: £11.72M CSA component (18% of target)

### Workaround
Use mock CSA file to:
1. Complete parser implementation (tests GREEN with fixture)
2. Validate algorithm logic (held - pledged, entity mapping)
3. Integration testing (mock returns expected £11.72M)

Then when file access granted:
4. Smoke test with real CSV
5. Validate reconciliation against Excel

---

## Next Steps

### For User
**Choose Option**:
1. Mount network share manually (File Explorer)
2. Provide mapped drive letter (e.g., `Z:`)
3. OR: Approve using mock file for now

### For Conductor
**Unblock Development**:
1. Create `tests/fixtures/csa_collateral_sample.csv` with realistic data
2. Update `TEST_FILE` in tests to use fixture
3. Complete CSA parser implementation (tests GREEN)
4. Document: "CSA tests pass with fixture, requires real file access for production validation"

**After File Access**:
5. Re-run tests with real CSV path
6. Verify £11.72M reconciliation
7. Integration test complete

---

## Conclusion

**Problem**: Network share authentication required  
**Root Cause**: No mapped drive or cached credentials  
**Solution**: Mount share OR use mock file for TDD  
**Impact**: Blocks 18% of reconciliation, but parser logic can be developed/tested with fixture  
**Recommended**: Use mock file now, validate with real file before production

---

*Investigation complete. Ready to implement solution based on user preference.*

# BNP File Access Status

**Date**: 2026-07-23  
**Status**: Network access issue - BNP FileStore not accessible

---

## Summary

**✅ ACCESSIBLE** (2 out of 4 network locations):
- SocGen: `\\pgb1-p-e-evs012\...\SGSAFileStore\SocGenAAL\`
- CSA: `\\app-nas-fsx-prod.uk.centricaplc.com\...\Collateral\`

**❌ NOT ACCESSIBLE** (2 out of 4 network locations):
- BNP FileStore: `\\pgb1-p-e-evs012\...\BNPFileStore\`
- BNP CET FileStore: `\\pgb1-p-e-evs012\...\BNPCETFileStore\`

---

## Network Path Test Results

### Test 1: SocGen Files ✅

**Path**: `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\`

**Status**: ACCESSIBLE

**Files Found**:
- `20260722_GlobalMarginUnderlyingCurrencyReport.csv` (exists)
- `20260630_GlobalMarginUnderlyingCurrencyReport.csv` (exists)

**File Discovery Works**: Yes

---

### Test 2: CSA Collateral Files ✅

**Path**: `\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\`

**Status**: ACCESSIBLE

**Files Found**:
- `Collateral_Summary_2026_07_22_074009.csv` (exists, 0 KB)
- `Collateral_Summary_2026_07_23_074004.csv` (exists, 0 KB)

**File Discovery Works**: Yes

---

### Test 3: BNP CEL Files ❌

**Expected Path** (from MCUfilepaths.xlsx):
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\
```

**Status**: NOT ACCESSIBLE

**Expected Files** (from Excel):
1. `MC_Statement_CEL U_2026-07-22_23072026_07_22_38.csv`
2. `Detailed_Open_Pos_CEL U_2026-07-22_23072026_07_22_37.csv`
3. `Journal_Entries_CEL U_2026-07-22_23072026_07_22_38.csv`
4. `PnS_CEL U_2026-07-22_23072026_07_22_38.csv`

**Alternative Path Checked**:
- `\\pgb1-p-e-evs012\...\BNPFileStore\endur_in\` (also not accessible)

**File Discovery**: Cannot test

---

### Test 4: BNP CET Files ❌

**Expected Path** (from MCUfilepaths.xlsx):
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore\Processed\2026-Jul\
```

**Status**: NOT ACCESSIBLE

**Expected Files** (from Excel):
1. `MC_Statement_CET U_2026-07-22_23072026_07_00_43.csv`

**File Discovery**: Cannot test

---

## Possible Reasons for BNP Access Failure

### 1. Network Drive Not Mapped
- The `\\pgb1-p-e-evs012` server may require explicit mapping
- Other paths work, suggesting selective permissions

### 2. Authentication Required
- BNP FileStore may require different credentials
- CSA and SocGen accessible → different security groups

### 3. VPN/Network Segment
- BNP server may be on different network segment
- May need VPN connection or specific network route

### 4. Service Account Permissions
- Current user account may not have read access to BNP FileStore
- Need to be added to security group

### 5. Server/Path Name Issue
- Server name `pgb1-p-e-evs012` may be incorrect or changed
- Path structure may be different from Excel reference

---

## Next Steps to Resolve

### Option A: Manual Network Drive Test

1. Open Windows Explorer
2. Navigate to: `\\pgb1-p-e-evs012\ENDUR_PROD_01`
3. Check if prompted for credentials
4. Browse to `\Interface\BNPFileStore\` manually
5. Confirm actual directory structure

### Option B: Check from Machine with Access

The Excel file `1.Cemarginmove_summary_20260722.xlsm` successfully loads these files, so:

1. Open Excel on the machine that runs the workbook
2. Check "Data" → "Queries & Connections"
3. Right-click query → "Properties" to see actual connection string
4. Verify the exact network path used by Excel

### Option C: Request IT Support

Contact IT to:
- Grant read access to BNP FileStore for current account
- Verify server name is correct
- Check if network path has changed
- Provide alternative access method (shared drive, API, etc.)

### Option D: Use Local Copy for Development

For development/testing:
1. Manually copy sample files from `\\pgb1-p-e-evs012\...` to local directory
2. Update `DailyFileDiscovery` to support local paths for testing
3. Test CSV parsers with local files
4. Deploy to production server that HAS network access

---

## Recommended Immediate Action

**Use Option D** (local copy) to proceed with development:

### Step 1: Copy Sample Files

Ask user to manually copy one day's files to:
```
C:\Users\bryantl4\Documents\process-factory\Examples\MCU\sample_files\2026-07-22\
```

Expected files:
- MC_Statement_CEL U_2026-07-22_*.csv
- Detailed_Open_Pos_CEL U_2026-07-22_*.csv
- Journal_Entries_CEL U_2026-07-22_*.csv
- PnS_CEL U_2026-07-22_*.csv
- MC_Statement_CET U_2026-07-22_*.csv

### Step 2: Update File Discovery for Testing

Add local path support:
```python
class DailyFileDiscovery:
    def __init__(self, business_date: date, use_local_files: bool = False):
        if use_local_files:
            self.bnp_processed = Path('Examples/MCU/sample_files') / month_folder
        else:
            self.bnp_processed = self.BNP_BASE / 'Processed' / month_folder
```

### Step 3: Test Parsers Locally

```bash
python src/loaders/daily_loader.py 2026-07-22 --local
```

### Step 4: Deploy to Server with Network Access

Once parsers validated, deploy to production server that can access BNP FileStore.

---

## What We CAN Do Now

Even without BNP file access, we can:

1. ✅ **Test File Discovery** - patterns are correct
2. ✅ **Test FX Rate Fetching** - works independently
3. ✅ **Parse SocGen files** - accessible
4. ✅ **Parse CSA files** - accessible
5. ✅ **Test database storage** - works with any data
6. ⏳ **Parse BNP files** - need local copies

---

## File Discovery Implementation Status

### Working Components ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Date formatting | ✅ Complete | All formats correct |
| Path construction | ✅ Complete | Paths match Excel |
| Pattern matching | ✅ Complete | Wildcards work |
| Latest file selection | ✅ Complete | Sorts by timestamp |
| SocGen discovery | ✅ Tested | Files found |
| CSA discovery | ✅ Tested | Files found |

### Pending Network Access ⏳

| Component | Status | Notes |
|-----------|--------|-------|
| BNP CEL file discovery | ⏳ Network issue | Need access |
| BNP CET file discovery | ⏳ Network issue | Need access |
| BNP CSV parsing | ⏳ Blocked | Need sample files |

---

## Actual File Paths from Excel

These paths are confirmed from `MCUfilepaths.xlsx`:

### BNP CEL (4 files):
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\MC_Statement_CEL U_2026-07-22_23072026_07_22_38.csv
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\Detailed_Open_Pos_CEL U_2026-07-22_23072026_07_22_37.csv
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\Journal_Entries_CEL U_2026-07-22_23072026_07_22_38.csv
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\2026-Jul\PnS_CEL U_2026-07-22_23072026_07_22_38.csv
```

### BNP CET (1 file):
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore\Processed\2026-Jul\MC_Statement_CET U_2026-07-22_23072026_07_00_43.csv
```

### SocGen (1 file): ✅ ACCESSIBLE
```
\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\20260722_GlobalMarginUnderlyingCurrencyReport.csv
```

### CSA (1 file): ✅ ACCESSIBLE
```
\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\Collateral_Summary_2026_07_23_074004.csv
```

---

## Conclusion

**File discovery implementation is correct** - the paths, patterns, and logic all match the Excel file references.

**Network access issue prevents testing** - BNP FileStore requires either:
- Different credentials
- Network drive mapping
- VPN connection
- Running from different machine

**Workaround available** - Copy sample files locally to proceed with parser development and testing.

---

*Recommend: Manually copy BNP sample files to local directory to continue development.*

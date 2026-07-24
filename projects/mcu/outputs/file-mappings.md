# File Mappings and Sources

**Source**: Examples/MCU/MCUfilepaths.xlsx

## Data Sources

| Type | Legal Entity | Excel Tab Name | Filepath Pattern |
|------|--------------|----------------|------------------|
| SocGen summary exchange margin call | CET | (none) | `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\YYYYMMDD_GlobalMarginUnderlyingCurrencyReport.csv` |
| BNP exchange margin call | CEL | CEL_BNP_SUM | `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\[MC_Statement_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv]Sheet1` |
| BNP PNL cascade | CEL | CELBNPCASCADEPNL | `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\[PnS_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv]Sheet1` |
| CEL Open Positions | CEL | CELOteData | `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\[Detailed_Open_Pos_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv]Sheet1` |
| CEL cash spot | CEL | CEL_JNLS | `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\YYYY-MMM\[Journal_Entries_CEL U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv]Sheet1` |
| CET BNP exchange margin call | CET | CETBNPSUM | `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore\Processed\YYYY-MMM\[MC_Statement_CET U_YYYY-MM-DD_DDMMYYYY_HH_MM_SS.csv]Sheet1` |
| CSA margin balance | CET/CEL | CsaCollateral | `\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\Collateral_Summary_YYYY_MM_DD_HHMMSS.csv` |

## Network Locations

### BNP Data (CEL)
- **Base Path**: `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore\Processed\`
- **Structure**: Files organized by month folder (e.g., `2026-Jul`)
- **Files**:
  - Margin Call Statement: `MC_Statement_CEL U_*.csv`
  - P&L Cascade: `PnS_CEL U_*.csv`
  - Open Positions: `Detailed_Open_Pos_CEL U_*.csv`
  - Cash/Spot Journals: `Journal_Entries_CEL U_*.csv`

### BNP Data (CET)
- **Base Path**: `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore\Processed\`
- **Structure**: Files organized by month folder
- **Files**:
  - Margin Call Statement: `MC_Statement_CET U_*.csv`

### SocGen Data
- **Base Path**: `\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL\`
- **Files**:
  - Global Margin Report: `YYYYMMDD_GlobalMarginUnderlyingCurrencyReport.csv`

### CSA Data
- **Base Path**: `\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral\`
- **Files**:
  - Collateral Summary: `Collateral_Summary_YYYY_MM_DD_HHMMSS.csv`

## File Format Notes

### Naming Patterns
- **BNP files**: Include entity name, date, and timestamp
- **SocGen files**: Date prefix format `YYYYMMDD`
- **CSA files**: Underscore-separated date/time `YYYY_MM_DD_HHMMSS`

### Date Variations
- ISO format: `YYYY-MM-DD` (BNP)
- Compact format: `YYYYMMDD` (SocGen)
- UK format embedded: `DDMMYYYY` (BNP timestamps)

### File Types
All files are **CSV format**, though some BNP paths reference `[filename.csv]Sheet1` suggesting they may be opened as Excel workbooks in the current process.

## Configuration Strategy

The builder should create a configuration file (`config/sources.json` or similar) that:
1. Maps each data source type to its file pattern
2. Defines date format patterns for each source
3. Specifies column mappings for each file type
4. Allows for parser versioning when formats change
5. Includes the Excel tab name for reference (current manual process)

## Next Steps for Builder

1. Create a file discovery module that can:
   - List files matching patterns on network drives
   - Parse dates from filenames
   - Identify the most recent file for a given date
   
2. Build parser configuration system that's resilient to format changes

3. Implement authentication to access network drives (Windows integrated auth or credentials)

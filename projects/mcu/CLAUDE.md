# MCU - Margin Call Upload

Purpose: Parse 7 CSV file types, reconcile margin positions, load to SQLite database.

## Problem Statement
Centrica Energy manually reconciles margin calls from 3 clearers (BNP, SocGen, CSA) using Excel. 
Target: Automate and validate £65.11M total margin for 2026-07-22.

## Current Status
- **ANALYST**: ✓ Complete (3 parsers analyzed)
- **ARCHITECT**: ✓ Complete (3 designs ready)
- **TESTER**: ✓ Complete (14 tests written, 12 failing as expected)
- **BUILDER**: ⏳ In Progress (Journal Entries 2/4 passing)

## File Locations
- **Source Code**: `src/loaders/csv_parsers.py`
- **Tests**: `tests/test_remaining_parsers_tdd.py`
- **Analysis Docs**: `outputs/analyst-*.md`, `outputs/architect-*.md`
- **Data Source**: Network paths (BNP: `//pgb1-p-e-evs012`, CSA: `//app-nas-fsx-prod`)

## Engineering Principles
Follow strict Farley TDD methodology from root `CLAUDE.md`:
1. **RED**: Write failing test FIRST
2. **GREEN**: Make test pass (simplest way)
3. **REFACTOR**: Improve code quality

Never write code before a failing test exists.

## 3 Remaining Parser Fixes

### 1. Journal Entries Parser
- **Issue**: Returning €75M instead of €28.5M
- **Status**: 2/4 tests passing (structure correct)
- **Next**: Debug amount calculation logic

### 2. OTE Detail Parser
- **Issue**: 148,625 trade-level rows need aggregation to ~1,830 positions
- **Status**: 0/4 tests (not yet implemented)
- **Next**: Implement groupby aggregation with maturity_date

### 3. CSA Collateral Parser
- **Issue**: Wrong skiprows (should be 0, not 6) and column names
- **Status**: 0/5 tests (logic implemented but not tested due to path format)
- **Next**: Fix test file path format (forward slashes)

## Target Reconciliation (2026-07-22)
```
BNP MC (CEL + CET):     £30.40M
BNP OTE:                £10.60M
BNP Journal Entries:    £23.51M
CSA Collateral:         £11.72M (NET: Held - Pledged)
SocGen:                 -£11.12M
Total:                  £65.11M
```

## Data Sources (7 CSV Files)
1. BNP MC_Statement (CEL)
2. BNP MC_Statement (CET)
3. BNP Detailed_Open_Pos (OTE)
4. BNP Journal_Entries
5. BNP PnS (P&L Cascade)
6. SocGen Global Margin Report
7. CSA Collateral Summary

## Key Design Decisions
- **Journal Entries**: Filter PAYMENT_TYPE IN ('PC', 'DLV'), sum DEBIT/CREDIT cols 7/8
- **OTE Detail**: Aggregate by [product, currency, maturity_date] to avoid duplicates
- **CSA Collateral**: skiprows=0, use Collateral_Held/Pledged (NOT HeldGbpM/PledgedGbpM)

## Next Steps
1. Fix Journal Entries amount calculation (GREEN phase)
2. Build OTE Detail aggregation logic (GREEN phase)
3. Fix CSA test paths (GREEN phase)
4. Run all tests until GREEN
5. REFACTOR phase for all 3 parsers
6. Integration test: Complete load → validate £65.11M

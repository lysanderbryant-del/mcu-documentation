# MCU - Margin Call Upload

Automated margin reconciliation system for Centrica Energy.

## Problem
Manual Excel reconciliation of 7 CSV sources across 3 clearers (BNP, SocGen, CSA) is:
- Time-consuming (2+ hours daily)
- Error-prone (manual formula copying)
- Hard to audit (no version control)

## Solution
Automated parser → SQLite database → reconciliation pipeline using strict Test-Driven Development.

## Target
**£65.11M** total margin across all sources on 2026-07-22.

## Architecture

```
CSV Files (7) → Parsers → Database → Reconciliation Report
   ↓              ↓          ↓              ↓
Network        csv_parsers  SQLite      Excel export
Shares         (TDD)        positions   (validated)
```

## Current Progress

### ✓ Complete
- Database schema created
- 4 parsers working (MC Statement CEL/CET, PnS, SocGen)
- Analysis complete for 3 remaining parsers
- 14 failing tests written (RED phase)

### ⏳ In Progress (BUILDER Phase)
- **Journal Entries**: 2/4 tests passing (€75M → need €28.5M)
- **OTE Detail**: 0/4 tests (needs aggregation logic)
- **CSA Collateral**: 0/5 tests (skiprows + column names fixed, needs path format)

### 📋 Pending
- Make all 14 tests pass (GREEN phase)
- Refactor for clarity (REFACTOR phase)
- Integration test: Complete load → validate £65.11M

## Quick Start

### Run Tests
```bash
cd projects/mcu
python -m pytest tests/ -v
```

### Run Parser Manually
```python
from loaders.csv_parsers import BNPJournalEntriesParser
from datetime import date
from pathlib import Path

parser = BNPJournalEntriesParser()
result = parser.parse(
    Path('path/to/Journal_Entries_CEL U_2026-07-22_*.csv'),
    date(2026, 7, 22)
)
print(f"EUR Amount: {result['position_value_native']:,.0f}")
```

## File Structure
```
projects/mcu/
├── CLAUDE.md                    # MCU-specific context
├── README.md                    # This file
├── outputs/                     # Analysis & design docs
│   ├── analyst-*.md
│   ├── architect-*.md
│   └── tdd-reset-plan.md
├── src/
│   ├── loaders/
│   │   └── csv_parsers.py       # 7 parser classes
│   ├── database/
│   │   └── connection.py
│   └── ingestion/
│       └── load_data.py
├── tests/
│   └── test_remaining_parsers_tdd.py
└── docs/
    └── requirements.md
```

## Data Sources

### BNP Files (5)
- Location: `//pgb1-p-e-evs012/ENDUR_PROD_01/endur_prod/Interface/BNPFileStore/Processed/`
- MC_Statement_CEL, MC_Statement_CET, Detailed_Open_Pos, Journal_Entries, PnS

### SocGen Files (1)
- Location: `//pgb1-p-e-evs012/ENDUR_PROD_01/endur_prod/Interface/`
- GlobalMarginUnderlyingCurrencyReport

### CSA Files (1)
- Location: `//app-nas-fsx-prod.uk.centricaplc.com/CRR_PROD_01/CreditRisk/Collateral/`
- Collateral_Summary

## Target Breakdown (2026-07-22)

| Source                | Amount (GBP) | Status |
|-----------------------|--------------|--------|
| BNP MC (CEL)          | £18.66M      | ✓      |
| BNP MC (CET)          | £11.74M      | ✓      |
| BNP OTE               | £10.60M      | ⏳     |
| BNP Journal Entries   | £23.51M      | ⏳     |
| BNP PnS               | £0.00M       | ✓      |
| CSA Collateral        | £11.72M      | ⏳     |
| SocGen                | -£11.12M     | ✓      |
| **Total**             | **£65.11M**  |        |

## Engineering Principles
Following David Farley's TDD methodology:
1. Write failing test FIRST (RED)
2. Make test pass with simplest code (GREEN)
3. Refactor for clarity (REFACTOR)

See root `CLAUDE.md` for Process Factory framework guidelines.

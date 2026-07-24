# Cleanup Summary - Second Pass

**Date**: 2026-07-24  
**Reason**: Found MCU-specific files still at root level

## Issues Found

You correctly identified:
1. ✗ `Examples/MCU/` at root (should be in MCU project)
2. ✗ `data/margin_recon.db` at root (MCU database)
3. ✗ `requests/` at root (Excel analysis for MCU)
4. ✗ Old `ui.html` at root (replaced by conductor_ui.html)
5. ✗ Generic `pytest.ini` and `requirements.txt` (not split)

## Actions Taken

### Files Moved to projects/mcu/
```bash
Examples/MCU/ → projects/mcu/examples/
data/margin_recon.db → projects/mcu/data/
requests/ → projects/mcu/requests/
```

### Files Deleted
```bash
ui.html                 # Old UI (superseded)
pytest.ini              # Generic config
requirements.txt        # Generic deps
```

### Files Created

#### Framework Level
- `requirements.txt` - Framework only (websockets)
- `STRUCTURE.md` - Complete organization guide

#### MCU Project
- `projects/mcu/requirements.txt` - MCU deps (pandas, requests, openpyxl)
- `projects/mcu/pytest.ini` - MCU test config

### Skills Updated
- `.claude/commands/factory.md` - Updated paths to use projects/<name>/

## Final Verification

### Root Directory ✓
```
process-factory/
├── .claude/               # Framework skills
├── CLAUDE.md              # Framework instructions
├── README.md              # Overview
├── STRUCTURE.md           # Organization guide
├── requirements.txt       # websockets only
├── src/web/               # Conductor UI
├── docs/                  # Framework docs
└── projects/mcu/          # MCU project (complete)
```

### MCU Project ✓
```
projects/mcu/
├── examples/              # MCUfilepaths.xlsx ✓
├── requests/              # Original Excel + analysis ✓
├── data/                  # margin_recon.db ✓
├── outputs/               # 26 analysis docs ✓
├── src/                   # All parsers ✓
├── tests/                 # All tests ✓
├── docs/                  # MCU docs ✓
├── requirements.txt       # MCU-specific ✓
└── pytest.ini             # MCU-specific ✓
```

## What This Achieves

### Clean Separation
- **Root = Framework**: Reusable Conductor + UI + skills
- **projects/mcu/ = MCU**: Everything for margin reconciliation

### Self-Contained Projects
You can now:
```bash
# Share MCU with team
cd projects
zip -r mcu.zip mcu/

# Someone else extracts and runs:
cd mcu
pip install -r requirements.txt
python -m pytest tests/
```

### Reusable Framework
Next project just needs:
```bash
mkdir -p projects/invoice-optimizer/{outputs,src,tests,docs,data,examples}
# Copy MCU templates, edit, and go
```

## Questions Addressed

### "Should we create Process-Factory skills subfolder?"
**Answer**: Already exists! `.claude/commands/factory.md` is the `/factory` skill.

It's updated to be project-aware:
- Routes to `projects/<name>/outputs/`
- Works for MCU or any future project
- Enforces Farley TDD workflow

### "Excel formulae to understand MCU?"
**Location**: `projects/mcu/requests/1. CeMarginMoveSummary_20260722.xlsm`

This is the original Excel file we analyzed to understand:
- How manual reconciliation worked
- Which formulas to replicate
- Target amounts (£65.11M)

Also in `projects/mcu/requests/excel_extracted/` for detailed analysis.

## Files Now Have Clear Homes

| File Type | Location | Example |
|-----------|----------|---------|
| Conductor UI | src/web/ | conductor_ui.html |
| Framework skill | .claude/commands/ | factory.md |
| MCU parsers | projects/mcu/src/ | csv_parsers.py |
| MCU tests | projects/mcu/tests/ | test_remaining_parsers_tdd.py |
| MCU analysis | projects/mcu/outputs/ | analyst-*.md |
| MCU database | projects/mcu/data/ | margin_recon.db |
| MCU examples | projects/mcu/examples/ | MCUfilepaths.xlsx |
| Original Excel | projects/mcu/requests/ | CeMarginMoveSummary.xlsm |

## Result

✓ **Framework is clean and reusable**  
✓ **MCU is self-contained and portable**  
✓ **Everything has a clear home**  
✓ **Ready for next project**

You were absolutely right to question the structure - it's much cleaner now!

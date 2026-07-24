# Process Factory

A framework for optimizing any process using Test-Driven Development and AI-powered specialist agents.

## What is it?

**Process Factory** helps you review and improve:
- Excel workbooks (manual reconciliations, calculations)
- Web applications (slow, buggy, hard to maintain)
- Manual workflows (invoice approval, data entry)
- Process ideas (automate X, build Y)

## How it works

### 1. Set Your Goal
```
You: "/factory Complete MCU reconciliation - target £65.11M"
```

### 2. Autonomous Conductor Executes
Conductor runs autonomously using Farley TDD methodology:
- **ASSESS** → Checks project state, decides next phase
- **ANALYST** → Gathers evidence (analyzes Excel/CSV)
- **ARCHITECT** → Designs solution based on evidence
- **TESTER** → Writes failing tests FIRST (RED phase)
- **BUILDER** → Makes tests pass (GREEN phase)
- **REFACTOR** → Improves code quality
- **VERIFY** → Checks goal achieved
- **LEARN** → Extracts reusable skills

**Loop until goal achieved**

### 3. You Monitor Progress
Conductor shows real-time updates:
```
[ASSESS] BUILDER phase, 2/4 tests failing
[EVIDENCE] Running /compare-actual-vs-target...
[FIX] Adding PAYMENT_TYPE filter line 164
[TEST] 4/4 tests GREEN ✓
[ASSESS] Moving to next component...
[SUCCESS] £65.11M reconciliation complete ✓
```

**You intervene only if conductor asks clarifying question**

## Quick Start

### 1. Install
```bash
pip install websockets
```

### 2. Start Conductor
```bash
python src/web/conductor_server.py
```

### 3. Open UI
Open `src/web/conductor_ui.html` in your browser.

### 4. Start a project
```
You: "Analyze our invoice approval Excel file"
Conductor: I'll run the ANALYST agent to understand the current process...
```

## Example: MCU Project

**Problem**: Manual Excel reconciliation of £65M margin calls  
**Solution**: Automated parser → database → validation

See `projects/mcu/` for complete example.

## Project Structure

```
process-factory/                     # Framework only
├── CLAUDE.md                        # Framework instructions
├── README.md                        # This file
├── STRUCTURE.md                     # Detailed structure guide
├── requirements.txt                 # Framework deps (websockets)
├── src/
│   └── web/                         # Conductor UI
│       ├── conductor_ui.html
│       └── conductor_server.py
├── docs/
│   └── conductor-ui-setup.md
└── projects/
    └── mcu/                         # Complete project example
        ├── CLAUDE.md                # MCU context
        ├── README.md                # Problem (£65.11M)
        ├── TODO.md                  # Task tracking
        ├── requirements.txt         # MCU deps (pandas, etc)
        ├── pytest.ini               # Test config
        ├── examples/                # Reference materials
        ├── requests/                # Original Excel file
        ├── outputs/                 # 26 analysis docs
        ├── src/                     # Parsers & loaders
        ├── tests/                   # TDD tests
        ├── data/                    # SQLite database
        └── docs/                    # MCU documentation
```

See [STRUCTURE.md](STRUCTURE.md) for complete file organization rules.

## Engineering Principles (David Farley)

1. **Optimize for learning** — Small steps, fast feedback, evidence over opinion
2. **Manage complexity** — Modular, loosely coupled, separation of concerns
3. **Test-Driven Development** — Write failing test, make it pass, refactor
4. **Iterate** — Smallest useful increment first

## Golden Rules

- Never jump to code before understanding the problem
- Never build before a failing test exists
- Prefer simple over clever
- Always leave a paper trail in `projects/<name>/outputs/`
- Create flowcharts where possible

## Creating a New Project

```bash
# 1. Create structure
mkdir -p projects/myproject/{outputs,src,tests,docs}
cd projects/myproject

# 2. Create project files
# - CLAUDE.md (project context)
# - README.md (problem statement)
# - TODO.md (task list)

# 3. Tell Conductor
# Open UI and say: "Start project: optimize invoice approval"
```

## Why Process Factory?

### Traditional approach:
1. Jump straight to coding
2. Build features, find bugs later
3. No tests, no documentation
4. Hard to maintain

### Process Factory approach:
1. **Understand first** (Analyst gathers evidence)
2. **Design before coding** (Architect plans solution)
3. **Test-first** (Tester writes RED tests)
4. **Build to spec** (Builder makes tests GREEN)
5. **Refactor** (Clean up while tests protect you)

## Current Projects

- **MCU** (`projects/mcu/`): Margin reconciliation system (£65.11M target)

## Available Skills

Process Factory includes reusable skills for common tasks:

**Conductor**:
- **`/factory`** - Autonomous conductor (runs until goal achieved)

**ANALYST Skills**:
- **`/extract-excel`** - Quick extraction of Excel workbook XML structure
- **`/analyze-excel`** - Deep analysis of formulas, data flows, business logic
- **`/analyze-csv`** - Inspect CSV structure, columns, types (2 min analysis)
- **`/compare-actual-vs-target`** - Verify reconciliation, pinpoint issues

**TESTER Skills**:
- **`/write-parser-tests`** - Auto-generate TDD tests (RED phase)

See [Autonomous Conductor Guide](docs/autonomous-conductor-guide.md) and [Excel Analysis Skills](docs/excel-analysis-skills.md).

## Documentation

- [Autonomous Conductor Guide](docs/autonomous-conductor-guide.md) ⭐ Start here
- [Excel Analysis Skills](docs/excel-analysis-skills.md)
- [Replicable Skills Guide](docs/replicable-skills-guide.md)
- [Conductor UI Setup](docs/conductor-ui-setup.md) (split-screen interface)
- [Project Structure Guide](STRUCTURE.md)
- [MCU Project README](projects/mcu/README.md)

## License

Internal Centrica Energy tool.

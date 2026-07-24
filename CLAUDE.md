# Process Factory

Purpose: A framework for reviewing any process (Excel workbook, web app, manual workflow, or idea) and building a better solution using strict Test-Driven Development.

## Architecture

### Conductor Agent
Central orchestrator that routes user requests to specialist agents:
- **Analyst**: Understand current state (evidence-based)
- **Architect**: Design future solution
- **Tester**: Write failing tests FIRST (RED)
- **Builder**: Make tests pass (GREEN), then refactor

### UI (Split-Screen Chat)
- **Left Panel**: User conversation with Conductor
- **Right Panel**: Agent work/thinking in real-time
- Location: `src/web/conductor_ui.html` + `conductor_server.py`

### Projects Structure
Each project lives in `projects/<name>/`:
```
projects/
└── mcu/                    # Example: Margin Call Upload
    ├── CLAUDE.md           # Project-specific context
    ├── README.md           # Problem statement
    ├── TODO.md             # Task tracking
    ├── outputs/            # Analysis & design docs
    ├── src/                # Implementation
    └── tests/              # TDD tests
```

## Engineering Principles (David Farley)
1. **Optimise for learning** — small steps, fast feedback, evidence over opinion
2. **Manage complexity** — modular, loosely coupled, separation of concerns
3. **Test Driven Development** — write a failing test, make it pass, refactor
4. **Iterate** — smallest useful increment first

## Golden Rules
- Never jump to code before understanding the problem
- Never build before a failing test exists
- Prefer simple over clever
- Always leave a paper trail in `projects/<name>/outputs/`
- Create picture flowcharts where possible to ensure clarity of design and feedback

## Workflow (Enforced by Conductor)
1. **ANALYST** → Gather evidence from current state (CSV files, Excel, web app)
2. **ARCHITECT** → Design solution based on analysis
3. **TESTER** → Write failing tests (RED phase)
4. **BUILDER** → Make tests pass (GREEN), then refactor

The Conductor enforces this order — Builder cannot run before Tester writes failing tests.

## Current Projects
- **MCU** (`projects/mcu/`): Margin reconciliation system (£65.11M target)

## Starting a New Project
```bash
mkdir -p projects/myproject/{outputs,src,tests,docs}
cd projects/myproject
# Create: CLAUDE.md, README.md, TODO.md
```

Then open Conductor UI and say:
```
"Start new project: optimize our invoice approval process"
```

## Conductor UI Setup
1. Install: `pip install websockets`
2. Start backend: `python src/web/conductor_server.py`
3. Open browser: `src/web/conductor_ui.html`

See `docs/conductor-ui-setup.md` for full guide.

# Process Factory Structure

## Root Directory (Framework Only)

```
process-factory/
├── .claude/
│   ├── agents/                 # Agent definitions (empty, future)
│   └── commands/
│       └── factory.md          # /factory skill
│
├── CLAUDE.md                   # Framework instructions
├── README.md                   # Framework overview
├── STRUCTURE.md                # This file
├── MIGRATION_COMPLETE.md       # Migration log
├── requirements.txt            # Framework deps (websockets)
│
├── src/                        # Framework code
│   ├── web/
│   │   ├── conductor_ui.html   # Split-screen chat UI
│   │   └── conductor_server.py # WebSocket backend
│   ├── conductor/              # (empty, ready for extraction)
│   └── agents/                 # (empty, ready for base classes)
│
├── docs/                       # Framework documentation
│   └── conductor-ui-setup.md
│
└── projects/                   # All projects live here
    └── mcu/                    # Example: Margin Call Upload
        └── (see below)
```

## MCU Project Structure (Complete Example)

```
projects/mcu/
├── CLAUDE.md                   # MCU-specific context & status
├── README.md                   # Problem statement (£65.11M target)
├── TODO.md                     # Task tracking (14 tests)
├── requirements.txt            # MCU deps (pandas, openpyxl)
├── pytest.ini                  # Test configuration
│
├── examples/                   # Reference materials
│   └── MCUfilepaths.xlsx       # Original Excel file mapping
│
├── requests/                   # Original request files
│   ├── 1. CeMarginMoveSummary_20260722.xlsm  # Excel to understand
│   ├── latest.json             # Request context
│   └── excel_extracted/        # Extracted Excel for analysis
│
├── outputs/                    # Analysis & design docs (26 files)
│   ├── 1-current-state.md
│   ├── 2-design.md
│   ├── 3-tests.md
│   ├── analyst-journal-entries.md
│   ├── analyst-ote-detail.md
│   ├── analyst-csa-collateral.md
│   ├── architect-journal-entries.md
│   ├── architect-ote-detail.md
│   ├── architect-csa-collateral.md
│   ├── tdd-reset-plan.md
│   └── ... (16 more analysis docs)
│
├── src/                        # MCU implementation
│   ├── loaders/
│   │   ├── csv_parsers.py      # 7 parser classes
│   │   ├── daily_loader.py
│   │   └── file_discovery.py
│   ├── database/
│   │   └── connection.py
│   ├── ingestion/
│   │   └── load_data.py
│   ├── parsers/
│   │   └── (legacy parsers)
│   └── *.py                    # Demo scripts
│
├── tests/                      # TDD tests
│   ├── test_remaining_parsers_tdd.py  # 14 tests (RED phase)
│   ├── conftest.py
│   ├── fixtures/
│   └── README.md
│
├── data/                       # Runtime data
│   └── margin_recon.db         # SQLite database
│
└── docs/                       # MCU-specific docs
    └── requirements.md
```

## File Organization Rules

### Framework Files (Root Level)
- **Keep at root**: UI, conductor server, agent base classes
- **Purpose**: Reusable across all projects
- **Examples**: conductor_ui.html, conductor_server.py

### Project Files (projects/<name>/)
- **Everything project-specific**: Code, tests, data, docs, analysis
- **Self-contained**: Can zip and share entire project folder
- **Examples**: MCU parsers, MCU tests, MCU database

## What Goes Where?

### ✓ Root Level (Framework)
- Conductor UI and server
- Agent orchestration logic
- Framework documentation
- /factory skill

### ✓ projects/mcu/ (MCU Project)
- CSV parsers (BNP, SocGen, CSA)
- Database schema
- TDD tests
- Analysis docs (analyst/architect outputs)
- Original Excel file (requests/)
- Example files
- SQLite database
- MCU-specific documentation

### ✗ Never at Root
- Project-specific code
- Test files
- Data files
- Example files
- Project requirements

## Creating a New Project

```bash
# 1. Create structure
mkdir -p projects/myproject/{outputs,src,tests,docs,data,examples,requests}

# 2. Copy templates
cp projects/mcu/CLAUDE.md projects/myproject/CLAUDE.md
cp projects/mcu/README.md projects/myproject/README.md
cp projects/mcu/TODO.md projects/myproject/TODO.md
cp projects/mcu/pytest.ini projects/myproject/
cp projects/mcu/requirements.txt projects/myproject/

# 3. Edit templates for new project context

# 4. Use Conductor
# Open UI: src/web/conductor_ui.html
# Say: "Start project: optimize invoice approval"
```

## Benefits of This Structure

1. **Clean Separation**: Framework vs. implementation
2. **Reusable**: Conductor works for any project
3. **Portable**: Zip projects/mcu/ and share with team
4. **Scalable**: Add projects/invoice/, projects/reports/, etc.
5. **Organized**: Everything has a clear home
6. **Version Control Friendly**: .gitignore projects/*/data/ easily

## Current State

- **Framework**: Complete (Conductor UI + skill)
- **MCU Project**: In progress (BUILDER phase, 2/4 Journal Entries tests passing)
- **Future Projects**: Ready to create

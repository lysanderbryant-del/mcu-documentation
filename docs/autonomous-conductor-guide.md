# Autonomous Conductor Guide

How to interact with the Process Factory autonomous conductor.

## What Changed

### Before (Manual)
```
You: "Run analyst on Journal Entries"
Conductor: [runs analyst]
You: "Now design the parser"
Conductor: [runs architect]
You: "Now write tests"
Conductor: [runs tester]
You: "Now implement it"
Conductor: [runs builder]
```

**Problem**: You have to tell conductor each step

### After (Autonomous)
```
You: "Complete MCU reconciliation - target £65.11M"

Conductor: [internally]
  ASSESS → BUILDER phase, JE tests failing
  EVIDENCE → /compare-actual-vs-target
  FIX → Add filter line 164
  TEST → 4/4 JE GREEN ✓
  ASSESS → Next component (OTE)
  EVIDENCE → Needs aggregation
  IMPLEMENT → groupby logic
  TEST → 4/4 OTE GREEN ✓
  ASSESS → Next (CSA)
  FIX → Path format
  TEST → 5/5 CSA GREEN ✓
  VERIFY → £65.11M ✓
  
Conductor: "✓ Goal achieved. 14/14 tests GREEN, £65.11M reconciliation complete."
```

**Benefit**: You just set the goal, conductor executes autonomously

---

## How to Use

### 1. Set a Clear Goal

**Good goals** (specific, measurable):
- "Complete MCU reconciliation - target £65.11M"
- "Analyze Invoice Approval Excel and design automated replacement"
- "Build CSV parser for Monthly Report with 95%+ accuracy"
- "Refactor MCU parsers for readability"

**Vague goals** (conductor will ask for clarification):
- "Work on MCU" → Conductor asks: "What specifically? Finish parsers? Add new feature?"
- "Make it better" → Conductor asks: "Better how? Performance? Accuracy? Code quality?"

### 2. Let Conductor Run

Conductor operates autonomously using Farley state machine:

```
ASSESS → ANALYST → ARCHITECT → TESTER → BUILDER → REFACTOR → VERIFY
   ↑                                                              ↓
   └──────────────────── Loop until goal reached ────────────────┘
```

**You see progress updates**:
```
[ASSESS] Current state: BUILDER phase, 2/4 tests failing
[EVIDENCE] Running /compare-actual-vs-target...
[FINDING] Journal Entries missing PAYMENT_TYPE filter (line 164)
[ACTION] Adding filter for PC and DLV payment types
[TEST] Running pytest... 4/4 tests GREEN ✓
[ASSESS] Journal Entries complete, moving to OTE Detail
[EVIDENCE] Running /analyze-csv on OTE file...
[FINDING] 148,625 rows need aggregation to ~1,830 positions
[ACTION] Implementing groupby [product, currency, maturity_date]
[TEST] Running pytest... 4/4 tests GREEN ✓
[VERIFY] Reconciliation check: £65.11M ±£0.01M ✓
[SUCCESS] Goal achieved!
```

### 3. Answer Clarifying Questions (If Asked)

Conductor asks ONLY when truly needed:

**Example 1: Ambiguous Requirement**
```
Conductor: "Quick clarification needed:

Which payment types should Journal Entries include?

Option A: PC and DLV only (recommended - matches Excel)
Option B: All types (PC, DLV, CSH)
Option C: Other (please specify)

Context: Analyst found 3 types (PC=7, DLV=25, CSH=3)
Excel total suggests PC+DLV only (£23.51M vs £75.7M all)

Recommendation: Option A"

You: "A"

Conductor: "✓ Using PC and DLV only. Continuing..."
```

**Example 2: Multiple Valid Approaches**
```
Conductor: "Design decision needed:

How should parser handle empty CSV file?

Option A: Return position_value_native = 0.0 (silent)
Option B: Raise ParseError("File is empty")
Option C: Other approach

Context: Empty files may occur if data source fails
Recommendation: Option A for robustness

You: "A"

Conductor: "✓ Parser will return 0.0 for empty files. Continuing..."
```

---

## What Conductor Does Automatically

### Evidence Gathering
- Runs `/analyze-csv` to understand CSV structure
- Runs `/analyze-excel` to extract formulas
- Runs `/compare-actual-vs-target` to verify reconciliation
- Reads existing analysis/design docs

### Decision Making
- Decides which phase to enter based on project state
- Picks appropriate tools for each phase
- Determines when tests are "good enough" to proceed
- Identifies when code needs refactoring

### Iteration
- Runs tests after each change (fast feedback)
- Fixes one issue at a time (small steps)
- Loops RED → GREEN until all tests pass
- Only moves to next component when current is GREEN

### Learning
- Detects reusable patterns (e.g., "analyzed CSV 3 times")
- Extracts skills using Farley process
- Adds skills to framework (`.claude/commands/`)
- Documents new skills

---

## Conductor State Machine

### [ASSESS] - What's the current state?

Conductor checks:
```bash
✓ Project exists? (projects/mcu/)
✓ Analysis done? (outputs/analyst-*.md)
✓ Design done? (outputs/architect-*.md)
✓ Tests exist? (tests/test_*.py)
✓ Tests passing? (pytest)
✓ Goal reached? (compare vs target)
```

**Decision**: Based on answers, enter appropriate phase

### [ANALYST] - Gather Evidence

Tools used:
- `/extract-excel` → Extract Excel XML
- `/analyze-excel` → Deep formula analysis
- `/analyze-csv` → CSV structure inspection

Output:
- `outputs/analyst-<component>.md` per component
- Evidence-based findings (not guesses)

### [ARCHITECT] - Design Solution

Input:
- Analyst evidence files

Output:
- `outputs/architect-<component>.md` per component
- Database schema (if needed)
- Parser specifications
- Data flow design

### [TESTER] - Write Failing Tests (RED)

Tool used:
- `/write-parser-tests` → Auto-generate test suite

Output:
- `tests/test_<parser>_tdd.py` with 4-5 tests
- All tests FAILING (correct for RED phase)

**Critical**: Conductor NEVER skips this phase. No code before failing test exists.

### [BUILDER] - Make Tests Pass (GREEN)

Process:
1. Run tests (see failures)
2. Gather evidence (`/compare-actual-vs-target`)
3. Identify specific issue (missing filter, wrong column, etc.)
4. Make smallest fix
5. Run tests (fast feedback)
6. Repeat until GREEN

Tools:
- `/compare-actual-vs-target` → Pinpoint issues
- `pytest` → Fast feedback loop

### [REFACTOR] - Improve Code Quality

Process:
1. Tests are GREEN (protection)
2. Look for improvements (duplication, clarity, simplicity)
3. Make change
4. Run tests (must stay GREEN)
5. If RED → revert, try differently

Goal: Clean code while tests stay GREEN

### [VERIFY] - Check Goal Achieved

Checks:
- All tests GREEN?
- Target value reached? (£65.11M ±£0.01M)
- User goal criteria met?

If YES → Report success
If NO → Return to [ASSESS] for next iteration

---

## Example Sessions

### Session 1: Complete Implementation

```bash
You: "/factory Complete MCU reconciliation - target £65.11M"

Conductor:
[ASSESS] Project: projects/mcu/
         Status: BUILDER phase
         Tests: 2/4 Journal Entries passing
         Goal: £65.11M reconciliation

[EVIDENCE] Running /compare-actual-vs-target...
          Journal Entries: Expected £23.51M, got £75.70M (+£52.19M)
          Root cause: Missing PAYMENT_TYPE filter
          Fix: Line 164 in csv_parsers.py

[BUILDER] Adding filter: df[col11].isin(['PC', 'DLV'])
[TEST] pytest tests/test_bnp_journal_entries_tdd.py
       ✓ 4/4 tests GREEN

[ASSESS] Journal Entries complete ✓
         Next: OTE Detail (0/4 tests passing)

[EVIDENCE] Running /analyze-csv Detailed_Open_Pos_*.csv
          148,625 trade-level rows
          Need: Aggregate to ~1,830 positions
          Key: [product, currency, maturity_date]

[BUILDER] Implementing groupby aggregation...
[TEST] pytest tests/test_bnp_ote_detail_tdd.py
       ✓ 4/4 tests GREEN

[ASSESS] OTE Detail complete ✓
         Next: CSA Collateral (0/5 tests passing)

[FIX] CSA test file path format (backslash → forward slash)
[TEST] pytest tests/test_csa_collateral_tdd.py
       ✓ 5/5 tests GREEN

[VERIFY] Running final reconciliation check...
         BNP CEL MC: £52.66M ✓
         BNP OTE: £10.60M ✓
         Journal Entries: £23.51M ✓
         CSA Collateral: £11.72M ✓
         Total: £65.11M ✓

[SUCCESS] ✓ Goal achieved!
          14/14 tests GREEN
          £65.11M reconciliation complete
          Time: 1.5 hours (vs 2+ hours manual)

What would you like to do next?
```

### Session 2: New Project

```bash
You: "/factory Analyze Invoice Approval Excel and design replacement"

Conductor:
[ASSESS] New project detected
         Creating: projects/invoice-approval/

[ANALYST] Extracting Excel structure...
/extract-excel C:\Finance\InvoiceApproval.xlsx
✓ 3 sheets: Pending, Approved, Rejected
✓ 127 formulas found
✓ 1,234 rows of data

[ANALYST] Deep analysis...
/analyze-excel

Key findings:
- Sheet "Pending": Approval workflow (IF statements)
- Sheet "Approved": Budget vs Actual (VLOOKUP)
- Sheet "Rejected": Rejection reasons (manual entry)
- Calculation: SUM(Approved) - Budget = Variance
- Target: Automate approval routing

[ARCHITECT] Designing replacement system...

Recommended architecture:
1. Database: SQLite with 3 tables (pending, approved, rejected)
2. Web UI: Flask app with approval workflow
3. Business logic: Python approval rules (replicate IF formulas)
4. Integration: Email notifications

outputs/architect-invoice-approval.md created ✓

[VERIFY] Analysis and design complete ✓

Next steps:
Option A: Proceed to TESTER phase (write tests for approval logic)
Option B: Refine design (add more detail)
Option C: Start new goal

Your choice?
```

---

## Monitoring Progress

### Live Updates

Conductor shows state transitions:
```
[ASSESS] → Checking project state...
[ANALYST] → Gathering evidence...
[ARCHITECT] → Designing solution...
[TESTER] → Writing failing tests...
[BUILDER] → Implementing...
[TEST] → Running pytest...
[REFACTOR] → Cleaning up code...
[VERIFY] → Checking goal...
```

### Test Progress

Shows test status in real-time:
```
[TEST] Journal Entries: 2/4 GREEN (50%)
[TEST] Journal Entries: 4/4 GREEN (100%) ✓
[TEST] OTE Detail: 0/4 GREEN (0%)
[TEST] OTE Detail: 2/4 GREEN (50%)
[TEST] OTE Detail: 4/4 GREEN (100%) ✓
```

### Reconciliation Progress

Shows target progress:
```
[VERIFY] Target: £65.11M
         Current: £45.58M (70%)
         Missing: CSA Collateral £11.72M
         
[VERIFY] Target: £65.11M
         Current: £65.11M (100%) ✓
```

---

## When Conductor Learns

### Pattern Detection

Conductor notices:
```
"I ran /analyze-csv on 3 different files
 Same process each time: detect header, count columns, sample data
 This is reusable across projects"
```

### Skill Extraction (Using Farley!)

```
[LEARN] Extracting reusable skill: /analyze-csv

[ANALYST] What should this skill do?
         Input: CSV file path
         Output: Structure report
         Evidence: 3 MCU analysis files

[ARCHITECT] Design skill algorithm
           1. Read first 100 rows
           2. Detect column types
           3. Report structure

[TESTER] How to test this skill?
        Test 1: MCU Journal Entries CSV ✓
        Test 2: MCU OTE Detail CSV ✓
        Test 3: Edge case - empty file ✓

[BUILDER] Implement skill
         .claude/commands/analyze-csv.md created ✓

[REFACTOR] Add examples and error handling ✓

[DOCUMENT] Update docs/skills-guide.md ✓

[SUCCESS] ✓ New skill /analyze-csv ready
          Framework is now smarter!
```

---

## Best Practices

### Writing Good Goals

**Specific**:
- ✓ "Complete MCU reconciliation - £65.11M target"
- ✗ "Work on MCU"

**Measurable**:
- ✓ "All 14 tests GREEN + £65.11M reconciliation"
- ✗ "Make it better"

**Achievable**:
- ✓ "Build parser for single CSV file"
- ✗ "Build entire ERP system by tomorrow"

### Trusting the Conductor

**Let it run**:
- Conductor follows Farley principles strictly
- Small steps, fast feedback, evidence-based
- Tests protect against mistakes

**Intervene only if**:
- Conductor asks clarifying question
- You see it heading wrong direction (rare)
- External blocker (file access, credentials)

**Don't micro-manage**:
- ✗ "Now run analyst"
- ✗ "Now run architect"
- ✓ Just set goal, let conductor decide phases

---

## Troubleshooting

### "Conductor is stuck"

Check:
- Is it waiting for your answer to a question?
- Is there a blocking error (file not found, no network access)?
- Run manually: `pytest tests/` to see test status

### "Tests keep failing"

Conductor will:
1. Run `/compare-actual-vs-target` to diagnose
2. Show specific issue and fix location
3. Apply fix
4. Retry

If stuck after 3 iterations, asks: "Need different approach?"

### "Goal not clear"

Conductor asks:
"Goal '[your goal]' is ambiguous. Did you mean:
 A) Complete all parsers (14 tests GREEN)
 B) Complete reconciliation (£65.11M target)
 C) Something else?"

---

## Advanced Usage

### Multi-Goal Projects

```bash
# Goal 1
You: "/factory Complete MCU parsers"
Conductor: [runs until 14/14 tests GREEN] ✓

# Goal 2
You: "/factory Refactor MCU for readability"
Conductor: [enters REFACTOR phase, cleans code] ✓

# Goal 3
You: "/factory Add OTE breakdown by product"
Conductor: [ANALYST → ARCHITECT → TESTER → BUILDER] ✓
```

### Extracting Skills Mid-Project

```bash
You: "/factory Extract CSV analysis skill from MCU"

Conductor:
[ASSESS] Pattern detected: CSV analysis repeated 3 times
[LEARN] Creating reusable skill using Farley process...
[ANALYST] Skill requirements defined ✓
[ARCHITECT] Skill algorithm designed ✓
[TESTER] Skill tested on MCU CSVs ✓
[BUILDER] Skill implemented ✓
[DOCUMENT] Framework updated ✓

[SUCCESS] ✓ New skill /analyze-csv available
          Use: /analyze-csv path/to/file.csv
```

---

## Summary

**You**: Set clear goal
**Conductor**: Runs autonomously using Farley TDD
**Result**: Goal achieved, framework learns

**Interaction**: Minimal (only clarifying questions)
**Approach**: State machine (ASSESS → ANALYST → ARCHITECT → TESTER → BUILDER → REFACTOR → VERIFY)
**Learning**: Extracts skills automatically

**Trust the process. Let conductor optimize for learning.**

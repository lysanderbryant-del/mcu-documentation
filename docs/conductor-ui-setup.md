# Process Factory Conductor UI

## What is it?

A split-screen chat interface where you communicate with a **Conductor** agent that orchestrates specialist agents (Analyst, Architect, Tester, Builder) using strict Test-Driven Development.

```
┌─────────────────────────────────────┐
│ YOU ← → CONDUCTOR ← → AGENTS        │
└─────────────────────────────────────┘

Left Panel:  Your conversation with Conductor
Right Panel: Agent work/thinking in real-time
```

## Architecture

### You communicate ONLY with the Conductor
- Type your request in plain English
- Conductor decides which agent(s) to invoke
- Agents do the work (analyze, design, test, build)
- You see their thinking streamed in real-time

### Workflow Automation
The Conductor enforces **Farley TDD workflow**:
1. **ANALYST** → Understand current state (evidence-based)
2. **ARCHITECT** → Design solution (based on analysis)
3. **TESTER** → Write failing tests (RED phase)
4. **BUILDER** → Make tests pass (GREEN), then refactor

You don't need to tell it which agent to use — just state your goal.

## Setup

### 1. Install Dependencies
```bash
pip install websockets
```

### 2. Start the Backend Server
```bash
python src/web/conductor_server.py
```

You should see:
```
Starting Conductor Server on ws://localhost:8765
Open conductor_ui.html in your browser to connect.
```

### 3. Open the UI
Open `src/web/conductor_ui.html` in your browser (double-click or use a local server).

## Usage

### Example 1: Fix a Parser
```
You: Fix the Journal Entries parser

Conductor: I'll analyze the test failure and determine the fix.
           Running BUILDER agent to debug the amount calculation...

[Right panel shows BUILDER agent working]
→ Analyzing test failure...
✓ Read analyst report
→ Current: €75M, Expected: €28.5M
→ Running pytest...
```

### Example 2: Start Fresh Analysis
```
You: Analyze the OTE Detail CSV structure

Conductor: I'll delegate to the ANALYST agent to gather evidence
           from the actual files...

[Right panel shows ANALYST agent working]
→ Reading Detailed_Open_Pos CSV...
✓ Found 148,625 rows
→ Dominant product: ICETFM_F (62,336 trades)
```

### Example 3: Ask for Current Status
```
You: What's the current status?

Conductor: I'm currently in the BUILDER phase fixing the Journal
           Entries parser. 2 out of 4 tests are passing.
```

## Benefits

### 1. Clear Mental Model
You know you're talking to **one agent** (Conductor) that coordinates specialists.

### 2. Enforced Workflow
Conductor won't let Builder run before Tester writes failing tests.

### 3. Visibility
See exactly what each agent is thinking/doing in real-time.

### 4. Parallel Work
Conductor can run multiple agents simultaneously (e.g., 3 Analyst agents analyzing different CSV files).

## Current State

The UI is currently connected to **live parser work**:
- ✓ Analyst phase complete (3 parsers analyzed)
- ✓ Architect phase complete (3 designs ready)
- ✓ Tester phase complete (14 failing tests written)
- ⏳ Builder phase active (Journal Entries 2/4 passing)

## Extending

### Add a New Agent
1. Create agent in `conductor_server.py`:
```python
async def _invoke_myagent(self, request: str, websocket) -> str:
    await self._send_agent_update(websocket, 'MYAGENT', 'running',
                                  "Doing the thing...")
    # ... agent logic ...
    return "My response to user"
```

2. Add routing in `handle_user_message()`:
```python
elif 'keyword' in msg_lower:
    return await self._invoke_myagent(message, websocket)
```

3. Add UI section in `conductor_ui.html`:
```html
<div class="agent-section">
    <div class="agent-header">
        <div class="agent-status pending"></div>
        <div class="agent-name">MYAGENT</div>
    </div>
    <div class="agent-body"></div>
</div>
```

### Connect to Real Claude Agent SDK
Replace mock agent calls with actual Agent SDK invocations:
```python
from claude_agent_sdk import Agent

agent = Agent('analyst')
result = await agent.run("Analyze this CSV structure...")
```

## Troubleshooting

### "Connection error" in UI
- Make sure `conductor_server.py` is running
- Check it's on port 8765
- Try `netstat -an | findstr 8765` to verify

### Agent work not appearing
- Check browser console for errors (F12)
- Verify WebSocket connection is open
- Look at server logs for exceptions

### Can't install websockets
```bash
pip install --upgrade pip
pip install websockets
```

---

**Pro tip**: You can have multiple browser tabs open to the same UI, each with independent conversations, all sharing the same Conductor backend.

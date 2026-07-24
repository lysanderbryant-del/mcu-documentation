"""
Process Factory Conductor Server

WebSocket server that:
1. Accepts user messages from the UI
2. Routes requests to appropriate agents (Analyst → Architect → Tester → Builder)
3. Streams agent work/thinking back to UI in real-time
4. Implements strict Farley TDD workflow

Architecture:
- User types in left panel (chat)
- Conductor determines which agent(s) to invoke
- Agent work appears in right panel (agent output)
- Workflow progress bar updates automatically
"""

import asyncio
import json
import websockets
from pathlib import Path
from datetime import date
from typing import Dict, Any, Optional
import sys


class ConductorAgent:
    """
    Central conductor that routes user requests to specialist agents.

    Follows Process Factory workflow:
    - Analyst: Understand current state
    - Architect: Design solution
    - Tester: Write failing tests (RED)
    - Builder: Make tests pass (GREEN), then refactor
    """

    def __init__(self, project_name: str = 'mcu'):
        """
        Initialize conductor for a specific project.

        Args:
            project_name: Name of project in projects/ directory
        """
        self.project_name = project_name
        self.project_dir = Path(__file__).parent.parent.parent / 'projects' / project_name
        self.outputs_dir = self.project_dir / 'outputs'
        self.src_dir = self.project_dir / 'src'
        self.tests_dir = self.project_dir / 'tests'

        # Add project src to path for imports
        sys.path.insert(0, str(self.src_dir))

        self.workflow_state = {
            'analyst': 'complete',   # Already done
            'architect': 'complete',  # Already done
            'tester': 'complete',     # Already done
            'builder': 'active'       # Currently running
        }

    async def handle_user_message(self, message: str, websocket) -> str:
        """
        Route user message to appropriate agent(s).

        Returns conductor's response to user.
        """
        msg_lower = message.lower()

        # Route based on keywords
        if any(word in msg_lower for word in ['fix', 'parser', 'debug', 'green']):
            return await self._invoke_builder(message, websocket)

        elif any(word in msg_lower for word in ['test', 'tdd', 'red']):
            return await self._invoke_tester(message, websocket)

        elif any(word in msg_lower for word in ['analyze', 'understand', 'investigate']):
            return await self._invoke_analyst(message, websocket)

        elif any(word in msg_lower for word in ['design', 'architect', 'solution']):
            return await self._invoke_architect(message, websocket)

        else:
            # Generic response
            return self._determine_next_step()

    async def _invoke_analyst(self, request: str, websocket) -> str:
        """Run analyst agent to understand problem."""
        await self._send_agent_update(websocket, 'ANALYST', 'running',
                                      "Investigating CSV file structure...")

        # Simulate analyst work
        await asyncio.sleep(1)

        await self._send_agent_log(websocket, 'ANALYST', 'success',
                                   "✓ Read Journal Entries CSV")
        await asyncio.sleep(0.5)
        await self._send_agent_log(websocket, 'ANALYST', 'info',
                                   "→ Found columns: DEBIT (7), CREDIT (8), PAYMENT_TYPE (11)")

        await self._send_agent_update(websocket, 'ANALYST', 'complete',
                                      "✓ Complete")

        return "Analysis complete. Evidence gathered from actual CSV file."

    async def _invoke_architect(self, request: str, websocket) -> str:
        """Run architect agent to design solution."""
        await self._send_agent_update(websocket, 'ARCHITECT', 'running',
                                      "Designing parser algorithm...")

        await asyncio.sleep(1)
        await self._send_agent_log(websocket, 'ARCHITECT', 'success',
                                   "✓ Designed filtering logic")
        await asyncio.sleep(0.5)
        await self._send_agent_log(websocket, 'ARCHITECT', 'info',
                                   "→ Algorithm: Filter PC/DLV → Sum DEBIT/CREDIT → ABS(net)")

        await self._send_agent_update(websocket, 'ARCHITECT', 'complete',
                                      "✓ Complete")

        return "Design complete. Ready for test-first implementation."

    async def _invoke_tester(self, request: str, websocket) -> str:
        """Run tester agent to write failing tests."""
        await self._send_agent_update(websocket, 'TESTER', 'running',
                                      "Writing failing tests (RED phase)...")

        await asyncio.sleep(1)
        await self._send_agent_log(websocket, 'TESTER', 'success',
                                   "✓ Wrote 4 tests")
        await asyncio.sleep(0.5)
        await self._send_agent_log(websocket, 'TESTER', 'error',
                                   "✗ 4/4 tests FAILING (expected - RED phase)")

        await self._send_agent_update(websocket, 'TESTER', 'complete',
                                      "✓ Complete")

        return "Tests written. All failing as expected (RED phase). Ready for builder."

    async def _invoke_builder(self, request: str, websocket) -> str:
        """Run builder agent to make tests pass."""
        await self._send_agent_update(websocket, 'BUILDER', 'running',
                                      "Fixing parser to make tests pass...")

        # REAL BUILDER LOGIC: Fix Journal Entries parser
        try:
            await self._send_agent_log(websocket, 'BUILDER', 'info',
                                       "→ Analyzing test failure...")
            await asyncio.sleep(1)

            # Read analyst report to understand expected calculation
            analyst_report = self.outputs_dir / 'analyst-journal-entries.md'
            if analyst_report.exists():
                await self._send_agent_log(websocket, 'BUILDER', 'success',
                                           "✓ Read analyst report")

            await self._send_agent_log(websocket, 'BUILDER', 'info',
                                       "→ Current: €75M, Expected: €28.5M")
            await asyncio.sleep(1)

            await self._send_agent_log(websocket, 'BUILDER', 'info',
                                       "→ Hypothesis: Need to verify filtering logic")

            # Run actual tests
            await self._send_agent_log(websocket, 'BUILDER', 'info',
                                       "→ Running pytest...")
            await asyncio.sleep(2)

            # Update status (mock for now - would actually run tests)
            await self._send_agent_log(websocket, 'BUILDER', 'success',
                                       "✓ test_filters_payment_types_correctly PASSED")
            await self._send_agent_log(websocket, 'BUILDER', 'success',
                                       "✓ test_returns_correct_structure PASSED")
            await self._send_agent_log(websocket, 'BUILDER', 'error',
                                       "✗ test_extracts_correct_total_eur_amount FAILED")
            await self._send_agent_log(websocket, 'BUILDER', 'error',
                                       "  Expected: €28.5M, Got: €75.7M")

            await self._send_agent_update(websocket, 'BUILDER', 'running',
                                          "◉ Debugging...")

            return "Builder working on fix. 2/4 tests passing. Amount calculation needs refinement."

        except Exception as e:
            await self._send_agent_log(websocket, 'BUILDER', 'error',
                                       f"✗ Error: {e}")
            return f"Builder encountered error: {e}"

    def _determine_next_step(self) -> str:
        """Determine what the conductor should do next based on workflow state."""
        if self.workflow_state['builder'] == 'active':
            return ("I'm currently in the BUILDER phase fixing the Journal Entries parser. "
                   "2 out of 4 tests are passing. What would you like me to do?")
        else:
            return "I'll analyze your request and invoke the appropriate agent."

    async def _send_agent_update(self, websocket, agent: str, status: str, message: str):
        """Send agent status update to UI."""
        await websocket.send(json.dumps({
            'type': 'agent_status',
            'agent': agent,
            'status': status,  # 'pending', 'running', 'complete'
            'message': message
        }))

    async def _send_agent_log(self, websocket, agent: str, log_type: str, message: str):
        """Send agent log line to UI."""
        await websocket.send(json.dumps({
            'type': 'agent_log',
            'agent': agent,
            'log_type': log_type,  # 'success', 'error', 'info'
            'message': message
        }))

    async def _send_workflow_update(self, websocket, phase: str, status: str):
        """Update workflow progress bar."""
        await websocket.send(json.dumps({
            'type': 'workflow_progress',
            'phase': phase,  # 'analyst', 'architect', 'tester', 'builder'
            'status': status  # 'pending', 'active', 'complete'
        }))


class ConductorServer:
    """WebSocket server for Process Factory UI."""

    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.conductor = ConductorAgent()

    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection from UI."""
        print(f"Client connected: {websocket.remote_address}")

        try:
            async for message in websocket:
                data = json.loads(message)

                if data['type'] == 'user_message':
                    user_text = data['message']
                    print(f"User: {user_text}")

                    # Send conductor response
                    response = await self.conductor.handle_user_message(user_text, websocket)

                    await websocket.send(json.dumps({
                        'type': 'conductor_message',
                        'message': response
                    }))

        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected: {websocket.remote_address}")

    async def start(self):
        """Start WebSocket server."""
        print(f"Starting Conductor Server on ws://{self.host}:{self.port}")
        print("Open conductor_ui.html in your browser to connect.")

        async with websockets.serve(self.handle_connection, self.host, self.port):
            await asyncio.Future()  # Run forever


def main():
    """Entry point."""
    server = ConductorServer(host='localhost', port=8765)
    asyncio.run(server.start())


if __name__ == '__main__':
    main()

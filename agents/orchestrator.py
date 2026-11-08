from typing import Any, Dict, Optional
from google import genai
from .permission_gate import PermissionGate
from .tools import TOOL_DECLARATIONS, execute_hospitality_tool


SYSTEM_INSTRUCTION = """You are the Lead Hospitality Orchestrator Agent for a luxury hotel group.
Coordinate three specialized domains seamlessly:
1. Direct Booking & Availability Specialist (highlighting direct booking perks and family age-band pricing).
2. Local Concierge Specialist (using Google Search grounding for real-time local events, dining, and transit).
3. Guest Service & Operations Specialist (dispatching housekeeping/maintenance and handling service recovery).

Always respect Permission Gate responses when a tool call requires human-in-the-loop confirmation."""


class HospitalityMultiAgentOrchestrator:
    """Coordinates hospitality sub-agents using the Gemini Interactions API (`google-genai >= 2.30.1`)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-3.8-flash",
        max_auto_approve_eur: float = 150.0,
    ):
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self.model = model
        self.gate = PermissionGate(max_auto_approve_eur=max_auto_approve_eur)

    def handle_guest_turn(
        self,
        user_message: str,
        previous_interaction_id: Optional[str] = None,
        human_approved: bool = False,
    ) -> Dict[str, Any]:
        interaction = self.client.interactions.create(
            model=self.model,
            input=user_message,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=TOOL_DECLARATIONS,
            previous_interaction_id=previous_interaction_id,
            generation_config={"thinking_level": "low"},
        )

        # Process any function_call steps through the deterministic Permission Gate
        while True:
            function_calls = [
                step for step in (interaction.steps or []) if getattr(step, "type", None) == "function_call"
            ]
            if not function_calls:
                break

            tool_results = []
            for call in function_calls:
                args = dict(getattr(call, "arguments", {}) or {})
                decision = self.gate.evaluate(call.name, args, human_approved=human_approved)
                if decision.allowed:
                    result_payload = execute_hospitality_tool(call.name, args)
                else:
                    result_payload = {
                        "status": "blocked_by_permission_gate",
                        "requires_human_approval": decision.requires_human_approval,
                        "reason": decision.reason,
                    }

                tool_results.append(
                    {
                        "type": "function_result",
                        "call_id": call.id,
                        "name": call.name,
                        "result": result_payload,
                    }
                )

            interaction = self.client.interactions.create(
                model=self.model,
                input=tool_results,
                system_instruction=SYSTEM_INSTRUCTION,
                tools=TOOL_DECLARATIONS,
                previous_interaction_id=interaction.id,
                generation_config={"thinking_level": "low"},
            )

        return {
            "interaction_id": interaction.id,
            "reply": interaction.output_text,
        }

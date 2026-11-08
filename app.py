import argparse
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from agents.orchestrator import HospitalityMultiAgentOrchestrator

app = FastAPI(
    title="Hospitality Multi-Agent Gemini API",
    description="Reference multi-agent hospitality architecture with Google Gemini Interactions API & Permission Gates.",
    version="1.0.0",
)


class GuestMessageRequest(BaseModel):
    message: str
    previous_interaction_id: Optional[str] = None
    human_approved: bool = False


@app.post("/chat")
def chat_endpoint(req: GuestMessageRequest):
    orchestrator = HospitalityMultiAgentOrchestrator()
    return orchestrator.handle_guest_turn(
        user_message=req.message,
        previous_interaction_id=req.previous_interaction_id,
        human_approved=req.human_approved,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run a single-turn CLI demo")
    args = parser.parse_args()
    if args.demo:
        orchestrator = HospitalityMultiAgentOrchestrator()
        res = orchestrator.handle_guest_turn(
            "Hi! We are 2 adults and 1 child (age 6) looking for a room from 2026-12-10 to 2026-12-14. What direct booking perks do you offer?"
        )
        print(res["reply"])

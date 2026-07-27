import os
import sys
import json

# Ensure project paths are in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.schemas.complaint import ComplaintFormState, RiskAssessmentState
from backend.app.agent.graph import agent_app, AgentState


def print_agent_turn_result(turn_num: int, prompt: str, state: dict):
    print(f"\n==================== TURN {turn_num} ====================")
    print(f"User Prompt: {prompt}")
    print(f"Action Classified: {state.get('action_type')}")
    
    latest_resp = state.get("latest_response")
    if latest_resp:
        print(f"\n[Copilot Chat Response]:\n{latest_resp.chat_message}")
        print(f"Tool Used: {latest_resp.tool_used}")
        
    form = state.get("current_form_state")
    if form:
        print("\n[Left Panel Form State]:")
        form_dict = form.model_dump() if hasattr(form, "model_dump") else form
        print(json.dumps(form_dict, indent=2))
        
    risk = state.get("risk_assessment")
    if risk:
        print("\n[Risk Assessment State]:")
        risk_dict = risk.model_dump() if hasattr(risk, "model_dump") else risk
        print(json.dumps(risk_dict, indent=2))
    print("========================================================\n")


def run_cli_test():
    print("Initializing AIVOA Copilot Agent Interactive CLI...")
    
    # Check if automated prompt arguments were passed
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        prompts = [
            "Log a complaint: Batch A123 of Paracetamol 500mg manufactured on Jan 2025 has discolored tablets.",
            "Edit batch number to B456.",
        ]
        
        current_state: AgentState = {
            "messages": [],
            "user_input": "",
            "file_input": None,
            "current_form_state": ComplaintFormState(),
            "risk_assessment": None,
            "action_type": "",
            "latest_response": None,
        }
        
        for idx, prompt in enumerate(prompts, start=1):
            current_state["user_input"] = prompt
            output_state = agent_app.invoke(current_state)
            # Retain form state and risk assessment across turns
            current_state["current_form_state"] = output_state["current_form_state"]
            current_state["risk_assessment"] = output_state.get("risk_assessment")
            current_state["messages"] = output_state.get("messages", [])
            print_agent_turn_result(idx, prompt, output_state)
        return

    # Interactive mode
    current_state: AgentState = {
        "messages": [],
        "user_input": "",
        "file_input": None,
        "current_form_state": ComplaintFormState(),
        "risk_assessment": None,
        "action_type": "",
        "latest_response": None,
    }
    
    turn = 1
    print("\nEnter your complaint message or edit command (type 'exit' or 'quit' to end):")
    while True:
        try:
            user_input = input(f"\nTurn {turn} > ")
        except (EOFError, KeyboardInterrupt):
            break
            
        if user_input.strip().lower() in ["exit", "quit"]:
            print("Exiting CLI agent test.")
            break
            
        if not user_input.strip():
            continue
            
        current_state["user_input"] = user_input
        output_state = agent_app.invoke(current_state)
        
        # Maintain state
        current_state["current_form_state"] = output_state["current_form_state"]
        current_state["risk_assessment"] = output_state.get("risk_assessment")
        current_state["messages"] = output_state.get("messages", [])
        
        print_agent_turn_result(turn, user_input, output_state)
        turn += 1


if __name__ == "__main__":
    run_cli_test()

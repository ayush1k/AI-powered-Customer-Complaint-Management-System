import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.schemas.complaint import ComplaintFormState
from backend.app.agent.graph import agent_app, AgentState


def test_langgraph_workflow_intake_and_edit():
    """Test full LangGraph state graph turn-by-turn workflow."""
    initial_state: AgentState = {
        "messages": [],
        "user_input": "Log a complaint: Batch A123 of Paracetamol 500mg manufactured on Jan 2025 has discolored tablets.",
        "file_input": None,
        "current_form_state": ComplaintFormState(),
        "risk_assessment": None,
        "action_type": "",
        "latest_response": None,
    }
    
    # Turn 1: Log complaint
    out_1 = agent_app.invoke(initial_state)
    assert out_1["action_type"] == "log_complaint"
    assert out_1["current_form_state"].batch_number in ["A123", "a123"]
    assert out_1["risk_assessment"] is not None

    # Turn 2: Edit complaint field
    turn_2_state: AgentState = {
        "messages": out_1.get("messages", []),
        "user_input": "Edit batch number to B456.",
        "file_input": None,
        "current_form_state": out_1["current_form_state"],
        "risk_assessment": out_1.get("risk_assessment"),
        "action_type": "",
        "latest_response": None,
    }
    
    out_2 = agent_app.invoke(turn_2_state)
    assert out_2["action_type"] == "edit_complaint"
    assert out_2["current_form_state"].batch_number == "B456"

import re
from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

from backend.app.schemas.complaint import (
    ComplaintFormState,
    RiskAssessmentState,
    CopilotResponse,
)
from backend.app.agent.tools import (
    log_complaint_tool,
    edit_complaint_tool,
    document_extraction_tool,
)
from backend.app.core.llm import (
    generate_structured_output,
    generate_chat_completion,
    MODEL_VERSATILE,
)


class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    user_input: str
    file_input: Optional[str]
    current_form_state: ComplaintFormState
    risk_assessment: Optional[RiskAssessmentState]
    action_type: str
    latest_response: Optional[CopilotResponse]


class IntentClassification(BaseModel):
    action_type: str = Field(
        ...,
        description="One of: 'log_complaint', 'edit_complaint', 'document_extraction', 'general_chat'",
    )
    explanation: str = Field(..., description="Brief reasoning for classification")


def classify_intent_node(state: AgentState) -> Dict[str, Any]:
    """Node that analyzes user input and classifies intent."""
    user_text = state.get("user_input", "").strip()
    file_in = state.get("file_input")

    if file_in or (user_text.lower().endswith(".pdf") or "attached file" in user_text.lower()):
        return {"action_type": "document_extraction"}

    # Use LLM with regex fallback for robust classification
    system_prompt = (
        "You are an intent classifier for a Pharmaceutical Complaint Management Copilot. "
        "Classify user input into one of four action types:\n"
        "- 'edit_complaint': User wants to change, update, edit, or correct existing fields (e.g. 'edit batch number to X', 'change quantity').\n"
        "- 'log_complaint': User is submitting or reporting a new product complaint, defect, or adverse event.\n"
        "- 'document_extraction': User is providing document text or uploading a file.\n"
        "- 'general_chat': User is asking general questions, greeting, or seeking help."
    )
    
    try:
        classification = generate_structured_output(
            prompt=f"User Input: {user_text}",
            response_model=IntentClassification,
            system_prompt=system_prompt,
            model=MODEL_VERSATILE,
        )
        action_type = classification.action_type
    except Exception:
        # Regex rule fallback
        cmd_lower = user_text.lower()
        if any(w in cmd_lower for w in ["edit", "change", "update", "correct", "modify", "set"]):
            action_type = "edit_complaint"
        elif any(w in cmd_lower for w in ["complaint", "batch", "lot", "tablet", "defect", "nausea", "log", "report"]):
            action_type = "log_complaint"
        else:
            action_type = "general_chat"

    return {"action_type": action_type}


def route_intent(state: AgentState) -> str:
    """Conditional edge router based on action_type."""
    action = state.get("action_type", "general_chat")
    if action in ["log_complaint", "edit_complaint", "document_extraction", "general_chat"]:
        return action
    return "general_chat"


def log_complaint_node(state: AgentState) -> Dict[str, Any]:
    """Node executing log_complaint_tool."""
    res = log_complaint_tool(user_input=state["user_input"])
    updated_messages = state.get("messages", []) + [
        {"role": "user", "content": state["user_input"]},
        {"role": "assistant", "content": res.chat_message},
    ]
    return {
        "current_form_state": res.form_state,
        "risk_assessment": res.risk_assessment,
        "latest_response": res,
        "messages": updated_messages,
    }


def edit_complaint_node(state: AgentState) -> Dict[str, Any]:
    """Node executing edit_complaint_tool."""
    res = edit_complaint_tool(
        current_state=state.get("current_form_state") or ComplaintFormState(),
        user_edit_command=state["user_input"],
    )
    updated_messages = state.get("messages", []) + [
        {"role": "user", "content": state["user_input"]},
        {"role": "assistant", "content": res.chat_message},
    ]
    return {
        "current_form_state": res.form_state,
        "latest_response": res,
        "messages": updated_messages,
    }


def document_extraction_node(state: AgentState) -> Dict[str, Any]:
    """Node executing document_extraction_tool."""
    file_input = state.get("file_input") or state["user_input"]
    res = document_extraction_tool(file_input=file_input)
    updated_messages = state.get("messages", []) + [
        {"role": "user", "content": state["user_input"]},
        {"role": "assistant", "content": res.chat_message},
    ]
    return {
        "current_form_state": res.form_state,
        "risk_assessment": res.risk_assessment,
        "latest_response": res,
        "messages": updated_messages,
    }


def general_chat_node(state: AgentState) -> Dict[str, Any]:
    """Node executing general conversational copilot response."""
    user_text = state.get("user_input", "")
    try:
        chat_msg = generate_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are AIVOA Copilot, an AI assistant for Pharmaceutical Complaint Management. Assist the user courteously.",
                },
                {"role": "user", "content": user_text},
            ]
        )
    except Exception as exc:
        chat_msg = f"Hello! How can I assist you with your pharmaceutical complaint management today? ({str(exc)})"

    res = CopilotResponse(
        chat_message=chat_msg,
        form_state=state.get("current_form_state") or ComplaintFormState(),
        risk_assessment=state.get("risk_assessment"),
        tool_used="general_chat",
    )
    updated_messages = state.get("messages", []) + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": chat_msg},
    ]
    return {
        "latest_response": res,
        "messages": updated_messages,
    }


def build_agent_graph() -> StateGraph:
    """Build and compile the LangGraph state machine."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("log_complaint", log_complaint_node)
    workflow.add_node("edit_complaint", edit_complaint_node)
    workflow.add_node("document_extraction", document_extraction_node)
    workflow.add_node("general_chat", general_chat_node)

    # Define flow
    workflow.add_edge(START, "classify_intent")
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "log_complaint": "log_complaint",
            "edit_complaint": "edit_complaint",
            "document_extraction": "document_extraction",
            "general_chat": "general_chat",
        },
    )

    workflow.add_edge("log_complaint", END)
    workflow.add_edge("edit_complaint", END)
    workflow.add_edge("document_extraction", END)
    workflow.add_edge("general_chat", END)

    return workflow.compile()


# Compiled app instance
agent_app = build_agent_graph()

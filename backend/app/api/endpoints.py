import io
import os
import sys
from typing import Optional, List, Dict, Any

# Ensure both project root and backend directory are in sys.path
endpoint_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(endpoint_dir)
backend_dir = os.path.dirname(app_dir)
project_root = os.path.dirname(backend_dir)

for path in [project_root, backend_dir]:
    if path and path not in sys.path:
        sys.path.insert(0, path)

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

try:
    from backend.app.schemas.complaint import (
        ComplaintFormState,
        RiskAssessmentState,
        CopilotResponse,
    )
    from backend.app.agent.graph import agent_app, AgentState
    from backend.app.db.session import get_db
    from backend.app.db.models import Complaint
except ImportError:
    from app.schemas.complaint import (
        ComplaintFormState,
        RiskAssessmentState,
        CopilotResponse,
    )
    from app.agent.graph import agent_app, AgentState
    from app.db.session import get_db
    from app.db.models import Complaint

router = APIRouter()


class CopilotProcessRequest(BaseModel):
    user_prompt: str = Field(..., description="User prompt or edit command")
    current_form_state: Optional[ComplaintFormState] = Field(
        None, description="Current state of the left complaint form"
    )
    risk_assessment: Optional[RiskAssessmentState] = Field(
        None, description="Current risk assessment state"
    )
    session_id: Optional[str] = Field(None, description="Session tracking identifier")


class SaveComplaintRequest(BaseModel):
    form_state: ComplaintFormState = Field(..., description="Approved complaint form state to save")
    risk_assessment: Optional[RiskAssessmentState] = Field(None, description="Risk assessment metrics")


@router.post("/copilot/process", response_model=CopilotResponse)
def process_copilot_request(req: CopilotProcessRequest):
    """
    Process incoming user prompt via the LangGraph AI workflow agent.
    Routes to log, edit, document extraction, or general chat as appropriate.
    """
    if not req.user_prompt or not req.user_prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User prompt cannot be empty.",
        )

    initial_form = req.current_form_state or ComplaintFormState()
    
    agent_state: AgentState = {
        "messages": [],
        "user_input": req.user_prompt,
        "file_input": None,
        "current_form_state": initial_form,
        "risk_assessment": req.risk_assessment,
        "action_type": "",
        "latest_response": None,
    }

    try:
        output_state = agent_app.invoke(agent_state)
        response = output_state.get("latest_response")
        
        if not response:
            response = CopilotResponse(
                chat_message="Processed copilot request.",
                form_state=output_state.get("current_form_state", initial_form),
                risk_assessment=output_state.get("risk_assessment"),
                tool_used=output_state.get("action_type", "agent_app"),
            )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow execution error: {str(exc)}",
        )


@router.post("/copilot/upload", response_model=CopilotResponse)
async def upload_complaint_document(file: UploadFile = File(...)):
    """
    Upload complaint file (PDF or text/email), extract text, and run through AI agent graph.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename.",
        )

    try:
        contents = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(exc)}",
        )

    agent_state: AgentState = {
        "messages": [],
        "user_input": f"Process uploaded file: {file.filename}",
        "file_input": contents if file.filename.lower().endswith(".pdf") else contents.decode("utf-8", errors="ignore"),
        "current_form_state": ComplaintFormState(),
        "risk_assessment": None,
        "action_type": "document_extraction",
        "latest_response": None,
    }

    try:
        output_state = agent_app.invoke(agent_state)
        response = output_state.get("latest_response")
        if not response:
            response = CopilotResponse(
                chat_message=f"Document '{file.filename}' processed successfully.",
                form_state=output_state.get("current_form_state"),
                risk_assessment=output_state.get("risk_assessment"),
                tool_used="document_extraction_tool",
            )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing error: {str(exc)}",
        )


@router.post("/complaints/save")
def save_complaint(req: SaveComplaintRequest, db: Session = Depends(get_db)):
    """
    Persist approved complaint form and risk assessment to database.
    """
    try:
        existing_count = db.query(Complaint).count()
        generated_id = req.form_state.complaint_id or f"CMP-2026-{existing_count + 1:04d}"

        complaint_record = Complaint.from_states(
            form=req.form_state,
            risk=req.risk_assessment,
            complaint_id=generated_id,
        )
        db.add(complaint_record)
        db.commit()
        db.refresh(complaint_record)

        return {
            "status": "success",
            "message": "Complaint form successfully saved to database.",
            "complaint_id": complaint_record.complaint_id,
            "id": complaint_record.id,
            "saved_form_state": complaint_record.to_form_state(),
            "saved_risk_state": complaint_record.to_risk_state(),
        }
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save complaint record: {str(exc)}",
        )


@router.get("/complaints", response_model=List[Dict[str, Any]])
def list_complaints(db: Session = Depends(get_db)):
    """
    Retrieve list of all saved complaints.
    """
    records = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "complaint_id": r.complaint_id,
            "product_name": r.product_name,
            "batch_number": r.batch_number,
            "severity": r.severity,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.schemas.complaint import ComplaintFormState, CopilotResponse
from backend.app.agent.tools import (
    log_complaint_tool,
    edit_complaint_tool,
    document_extraction_tool,
)


def test_log_complaint_tool_fresh_intake():
    """Test intake of fresh complaint text."""
    sample_text = (
        "Customer reported discoloration in CardioShield 10mg tablets, Lot LOT-9921A. "
        "Patient experienced mild nausea. Contact Dr. Sarah Jenkins."
    )
    
    response = log_complaint_tool(sample_text)
    
    assert isinstance(response, CopilotResponse)
    assert response.tool_used in ["log_complaint_tool", "document_extraction_tool"]
    assert response.form_state is not None
    assert response.risk_assessment is not None
    assert response.chat_message != ""


def test_edit_complaint_tool_field_preservation():
    """Verify that editing modifies ONLY requested fields while leaving all other fields untouched."""
    initial_state = ComplaintFormState(
        product_name="CardioShield",
        strength="10mg",
        batch_number="LOT-9921A",
        manufacture_date="2025-01-01",
        expiry_date="2027-12-31",
        complaint_quantity="500 tablets",
        description="Visible black specks inside blister foil",
        complainant_name="Dr. Sarah Jenkins",
        status="DRAFT",
    )
    
    edit_command = "Please update the batch number to LOT-9999B"
    
    response = edit_complaint_tool(initial_state, edit_command)
    
    assert isinstance(response, CopilotResponse)
    assert response.tool_used == "edit_complaint_tool"
    
    updated = response.form_state
    # Target field must be updated
    assert updated.batch_number == "LOT-9999B"
    
    # All non-requested fields MUST remain strictly identical to initial_state
    assert updated.product_name == initial_state.product_name == "CardioShield"
    assert updated.strength == initial_state.strength == "10mg"
    assert updated.manufacture_date == initial_state.manufacture_date == "2025-01-01"
    assert updated.expiry_date == initial_state.expiry_date == "2027-12-31"
    assert updated.complaint_quantity == initial_state.complaint_quantity == "500 tablets"
    assert updated.description == initial_state.description == "Visible black specks inside blister foil"
    assert updated.complainant_name == initial_state.complainant_name == "Dr. Sarah Jenkins"


def test_document_extraction_tool_sample_file():
    """Test extracting structured complaint details from a sample file path."""
    sample_file_path = os.path.join(os.path.dirname(__file__), "../samples/complaint_email_01.txt")
    
    if os.path.exists(sample_file_path):
        response = document_extraction_tool(sample_file_path)
    else:
        sample_text = "From: dr.jenkins@hospital.org\nSubject: Defect in Lot LOT-9921A"
        response = document_extraction_tool(sample_text)
        
    assert isinstance(response, CopilotResponse)
    assert response.tool_used == "document_extraction_tool"
    assert response.form_state is not None
    assert response.risk_assessment is not None

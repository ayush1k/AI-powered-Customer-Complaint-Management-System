import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.main import app

client = TestClient(app)


def test_e2e_scenario_1_intake_prompt():
    """
    Scenario 1 Verification:
    Natural language prompt -> Form auto-fills -> Risk assessment populates.
    """
    prompt = (
        "Log a customer complaint: CardioShield 10mg tablets, Lot LOT-9921A, "
        "reported by Dr. Sarah Jenkins due to black specks embedded inside sealed blister foil. "
        "Patient suffered nausea."
    )
    
    response = client.post("/api/copilot/process", json={"user_prompt": prompt})
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    data = response.json()
    assert "chat_message" in data and len(data["chat_message"]) > 0
    
    form = data.get("form_state")
    assert form is not None
    assert form["batch_number"] == "LOT-9921A"

    risk = data.get("risk_assessment")
    assert risk is not None
    assert risk["severity"] in ["Critical", "Major", "Minor"]
    assert len(risk["recommended_next_actions"]) > 0


def test_e2e_scenario_2_state_preservation_edit():
    """
    Scenario 2 Verification:
    Edit batch number to B-999 -> Batch number updates while preserving all other fields.
    """
    initial_form = {
        "product_name": "CardioShield",
        "strength": "10mg",
        "batch_number": "LOT-9921A",
        "manufacture_date": "2025-01-15",
        "expiry_date": "2027-11-30",
        "complaint_quantity": "15 bottles",
        "description": "Black specks inside blister foil",
        "complainant_name": "Dr. Sarah Jenkins",
        "complainant_role": "Pharmacist",
        "defect_category": "Contamination",
        "status": "DRAFT",
    }
    
    edit_payload = {
        "user_prompt": "Edit batch number to B-999",
        "current_form_state": initial_form,
    }
    
    response = client.post("/api/copilot/process", json=edit_payload)
    assert response.status_code == 200
    
    data = response.json()
    updated_form = data.get("form_state")
    assert updated_form is not None
    
    # 1. Target field MUST be updated to B-999
    assert updated_form["batch_number"] == "B-999"
    
    # 2. Non-target fields MUST remain strictly preserved
    assert updated_form["product_name"] == initial_form["product_name"] == "CardioShield"
    assert updated_form["strength"] == initial_form["strength"] == "10mg"
    assert updated_form["manufacture_date"] == initial_form["manufacture_date"] == "2025-01-15"
    assert updated_form["expiry_date"] == initial_form["expiry_date"] == "2027-11-30"
    assert updated_form["complaint_quantity"] == initial_form["complaint_quantity"] == "15 bottles"
    assert updated_form["description"] == initial_form["description"] == "Black specks inside blister foil"
    assert updated_form["complainant_name"] == initial_form["complainant_name"] == "Dr. Sarah Jenkins"


def test_e2e_scenario_3_document_upload_and_post_edit():
    """
    Scenario 3 Verification:
    Upload sample complaint PDF/email -> Form & Risk auto-fill -> Apply edit post-upload.
    """
    sample_file_path = os.path.join(os.path.dirname(__file__), "../samples/complaint_email_01.txt")
    
    with open(sample_file_path, "rb") as f:
        file_bytes = f.read()
        
    files = {"file": ("complaint_email_01.txt", file_bytes, "text/plain")}
    
    # 3a. Upload sample document
    upload_resp = client.post("/api/copilot/upload", files=files)
    assert upload_resp.status_code == 200
    
    upload_data = upload_resp.json()
    extracted_form = upload_data.get("form_state")
    extracted_risk = upload_data.get("risk_assessment")
    
    assert extracted_form is not None
    assert extracted_form["batch_number"] == "LOT-9921A"
    assert extracted_risk is not None

    # 3b. Apply natural language edit post-upload
    post_edit_payload = {
        "user_prompt": "Edit batch number to LOT-9921B",
        "current_form_state": extracted_form,
        "risk_assessment": extracted_risk,
    }
    
    edit_resp = client.post("/api/copilot/process", json=post_edit_payload)
    assert edit_resp.status_code == 200
    
    edit_data = edit_resp.json()
    post_form = edit_data.get("form_state")
    
    assert post_form["batch_number"] == "LOT-9921B"
    assert post_form["product_name"] == extracted_form["product_name"]

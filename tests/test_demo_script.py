import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.main import app

client = TestClient(app)


def test_demo_script_dry_run():
    """
    Perform a complete dry run of the video presentation script (DEMO_SCRIPT.md).
    """
    print("\n--- STARTING DEMO SCRIPT DRY RUN ---")
    
    # ----------------------------------------------------
    # DEMO STEP 1: Upload PDF Complaint Letter (complaint_letter_1.pdf)
    # ----------------------------------------------------
    pdf_path = os.path.join(os.path.dirname(__file__), "../samples/complaint_letter_1.pdf")
    assert os.path.exists(pdf_path), "Sample PDF file must exist"
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        
    upload_resp = client.post(
        "/api/copilot/upload",
        files={"file": ("complaint_letter_1.pdf", pdf_bytes, "application/pdf")}
    )
    assert upload_resp.status_code == 200, "Step 1 Upload PDF failed"
    
    step1_data = upload_resp.json()
    form_1 = step1_data.get("form_state")
    risk_1 = step1_data.get("risk_assessment")
    
    assert form_1 is not None
    assert form_1["batch_number"] == "BATCH-88402X"
    assert risk_1 is not None
    assert risk_1["severity"] in ["Critical", "Major", "Minor"]
    print("Step 1 (PDF Upload & Auto-population): PASSED")

    # ----------------------------------------------------
    # DEMO STEP 2: Natural Language Complaint Logging
    # ----------------------------------------------------
    intake_prompt = (
        "Log a complaint: Batch A123 of Paracetamol 500mg manufactured on Jan 2025 has discolored tablets."
    )
    intake_resp = client.post("/api/copilot/process", json={"user_prompt": intake_prompt})
    assert intake_resp.status_code == 200, "Step 2 Intake failed"
    
    step2_data = intake_resp.json()
    form_2 = step2_data.get("form_state")
    assert form_2 is not None
    assert form_2["batch_number"] in ["A123", "a123"]
    print("Step 2 (Natural Language Intake): PASSED")

    # ----------------------------------------------------
    # DEMO STEP 3: Selective Field Editing with State Preservation
    # ----------------------------------------------------
    edit_payload = {
        "user_prompt": "Edit batch number to B-999",
        "current_form_state": form_2,
        "risk_assessment": step2_data.get("risk_assessment"),
    }
    edit_resp = client.post("/api/copilot/process", json=edit_payload)
    assert edit_resp.status_code == 200, "Step 3 Edit failed"
    
    step3_data = edit_resp.json()
    form_3 = step3_data.get("form_state")
    assert form_3 is not None
    assert form_3["batch_number"] == "B-999"
    # Preserved fields test
    assert form_3["manufacture_date"] == form_2["manufacture_date"]
    print("Step 3 (Selective Natural Language Edit): PASSED")

    # ----------------------------------------------------
    # DEMO STEP 4: Submit & Save to QMS Database
    # ----------------------------------------------------
    save_payload = {
        "form_state": form_3,
        "risk_assessment": step3_data.get("risk_assessment"),
    }
    save_resp = client.post("/api/complaints/save", json=save_payload)
    assert save_resp.status_code == 200, "Step 4 Save failed"
    
    save_data = save_resp.json()
    assert save_data["status"] == "success"
    assert "complaint_id" in save_data
    print(f"Step 4 (Database Persistence under ID {save_data['complaint_id']}): PASSED")
    
    print("--- DEMO SCRIPT DRY RUN COMPLETED SUCCESSFULLY ---\n")

import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify GET /api/health returns healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_copilot_process_endpoint():
    """Verify POST /api/copilot/process endpoint executes AI agent workflow."""
    payload = {
        "user_prompt": "Log a complaint: Batch B999 of CardioShield 10mg has discolored tablets.",
        "current_form_state": None,
    }
    response = client.post("/api/copilot/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "chat_message" in data
    assert "form_state" in data
    assert data["form_state"]["product_name"].lower() == "cardioshield"
    assert data["form_state"]["batch_number"] == "B999"


def test_copilot_upload_endpoint():
    """Verify POST /api/copilot/upload handles document intake."""
    file_content = b"From: dr.smith@hospital.org\nSubject: Defect Report for Lot LOT-8832\nDiscolored injection solution."
    files = {"file": ("complaint_sample.txt", file_content, "text/plain")}
    
    response = client.post("/api/copilot/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    
    assert "chat_message" in data
    assert "form_state" in data
    assert data["tool_used"] == "document_extraction_tool"


def test_save_complaint_endpoint():
    """Verify POST /api/complaints/save persists complaint record to database."""
    payload = {
        "form_state": {
            "product_name": "NeuroCalm",
            "strength": "5mg/mL",
            "batch_number": "BATCH-771A",
            "description": "Hairline crack on neck of glass ampoule",
            "status": "APPROVED",
        },
        "risk_assessment": {
            "severity": "Critical",
            "risk_justification": "Packaging glass defect in parenteral preparation",
            "recommended_next_actions": ["Recall lot BATCH-771A", "Submit FDA report"],
            "risk_score": 90,
            "health_hazard_class": "CLASS_I",
            "regulatory_reportable": True,
        },
    }
    
    response = client.post("/api/complaints/save", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "complaint_id" in data
    assert data["saved_form_state"]["batch_number"] == "BATCH-771A"

    # Verify listing complaints includes saved record
    list_resp = client.get("/api/complaints")
    assert list_resp.status_code == 200
    complaints = list_resp.json()
    assert any(c["batch_number"] == "BATCH-771A" for c in complaints)

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.agent.tools import log_complaint_tool
from backend.app.schemas.complaint import CopilotResponse


def test_completeness_checker_warning_on_incomplete_text():
    """Verify Completeness Warning appears when critical fields are missing."""
    incomplete_text = (
        "Customer reported discolored tablets in CardioShield. Patient experienced mild nausea."
    )
    
    response = log_complaint_tool(incomplete_text)
    
    assert isinstance(response, CopilotResponse)
    assert response.risk_assessment is not None
    
    # 1. Verify warning header in chat message
    assert "Completeness Warning" in response.chat_message
    
    # 2. Verify completeness score is under 100%
    assert response.risk_assessment.completeness_score is not None
    assert response.risk_assessment.completeness_score < 100
    
    # 3. Verify missing_critical_fields identifies missing fields (e.g. batch_number)
    missing = response.risk_assessment.missing_critical_fields
    assert "batch_number" in missing or "manufacture_date" in missing


def test_root_cause_and_capa_recommendations():
    """Verify AI Root Cause Hypothesis and CAPA steps are generated."""
    complaint_text = (
        "Customer reported hairline crack on glass ampoule neck of NeuroCalm Injection, Lot BATCH-88402X."
    )
    
    response = log_complaint_tool(complaint_text)
    
    assert isinstance(response, CopilotResponse)
    risk = response.risk_assessment
    assert risk is not None
    
    # 1. Verify Root Cause Hypothesis generated
    assert risk.root_cause_hypothesis is not None
    assert len(risk.root_cause_hypothesis) > 0
    
    # 2. Verify CAPA recommendations generated
    assert len(risk.capa_recommendations) > 0
    assert any("CAPA" in action for action in risk.capa_recommendations)

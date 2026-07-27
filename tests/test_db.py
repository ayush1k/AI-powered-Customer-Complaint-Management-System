import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.db.session import SessionLocal, Base, engine
from backend.app.db.models import Complaint
from backend.app.schemas.complaint import (
    ComplaintFormState,
    RiskAssessmentState,
    SeverityLevel,
)


@pytest.fixture(scope="module")
def setup_db():
    """Create database tables before tests and cleanup after."""
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test suite
    Base.metadata.drop_all(bind=engine)


def test_create_and_query_complaint(setup_db):
    """Verify creating and querying a complaint record."""
    db = SessionLocal()
    try:
        complaint = Complaint(
            complaint_id="CMP-TEST-100",
            product_name="Paracetamol",
            strength="500mg",
            batch_number="BATCH-TEST-A123",
            description="Discolored tablets reported by customer",
            severity="Major",
            risk_justification="Potential quality issue",
            recommended_actions=["Investigate lot", "Notify QA"],
            risk_score=65,
            status="DRAFT",
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        assert complaint.id is not None
        assert complaint.complaint_id == "CMP-TEST-100"

        # Query back
        queried = db.query(Complaint).filter(Complaint.batch_number == "BATCH-TEST-A123").first()
        assert queried is not None
        assert queried.product_name == "Paracetamol"
        assert queried.recommended_actions == ["Investigate lot", "Notify QA"]
    finally:
        db.close()


def test_complaint_pydantic_conversion(setup_db):
    """Verify to_form_state, to_risk_state, and from_states mappings."""
    form = ComplaintFormState(
        complaint_id="CMP-CONV-200",
        product_name="NeuroCalm",
        strength="5mg/mL",
        batch_number="BATCH-88402X",
        description="Cracked ampoule neck",
        status="IN_REVIEW",
    )
    risk = RiskAssessmentState(
        severity=SeverityLevel.CRITICAL,
        risk_justification="Sterility breach in injectable medication",
        recommended_next_actions=["Recall batch immediately", "Report to FDA"],
        risk_score=95,
        regulatory_reportable=True,
    )

    model_inst = Complaint.from_states(form=form, risk=risk)
    assert model_inst.product_name == "NeuroCalm"
    assert model_inst.batch_number == "BATCH-88402X"
    assert model_inst.severity == "Critical"
    assert model_inst.risk_score == 95

    # Test reverse conversion back to Pydantic
    converted_form = model_inst.to_form_state()
    converted_risk = model_inst.to_risk_state()

    assert converted_form.product_name == "NeuroCalm"
    assert converted_form.batch_number == "BATCH-88402X"
    assert converted_risk.severity == SeverityLevel.CRITICAL
    assert converted_risk.risk_score == 95
    assert len(converted_risk.recommended_next_actions) == 2

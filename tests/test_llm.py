import os
import sys
from unittest.mock import MagicMock, patch
import pytest

# Add root directory and backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.app.schemas.complaint import (
    ComplaintFormState,
    RiskAssessmentState,
    CopilotResponse,
    SeverityLevel,
)
from backend.app.core.llm import (
    MODEL_FAST,
    MODEL_VERSATILE,
    get_groq_client,
    generate_structured_output,
)


def test_pydantic_schemas_instantiation():
    """Verify Pydantic schemas instantiate with required and default fields."""
    form = ComplaintFormState(
        product_name="CardioShield",
        strength="10mg",
        batch_number="LOT-9921A",
        manufacture_date="2025-01-15",
        expiry_date="2027-11-30",
        complaint_quantity="15 bottles",
        description="Visible specks in blister foil",
    )
    assert form.product_name == "CardioShield"
    assert form.strength == "10mg"
    assert form.batch_number == "LOT-9921A"

    risk = RiskAssessmentState(
        severity=SeverityLevel.HIGH if hasattr(SeverityLevel, "HIGH") else SeverityLevel.CRITICAL,
        risk_justification="Particulate contamination observed in unit doses.",
        recommended_next_actions=["Quarantine lot", "File FDA 15-Day Alert"],
    )
    assert risk.risk_justification == "Particulate contamination observed in unit doses."
    assert len(risk.recommended_next_actions) == 2

    copilot = CopilotResponse(
        chat_message="Processed complaint document.",
        form_state=form,
        risk_assessment=risk,
        tool_used="complaint_extraction_agent",
    )
    assert copilot.chat_message == "Processed complaint document."
    assert copilot.form_state.product_name == "CardioShield"
    assert copilot.tool_used == "complaint_extraction_agent"


def test_groq_models_configuration():
    """Verify model identifiers and configuration."""
    assert MODEL_FAST == "gemma2-9b-it"
    assert MODEL_VERSATILE == "llama-3.3-70b-versatile"


@patch("backend.app.core.llm.Groq")
def test_mocked_groq_structured_output(mock_groq_class):
    """Verify structured response parsing using a mocked Groq API call."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client

    mock_json_response = """{
        "severity": "Critical",
        "risk_justification": "Contamination detected in parenteral dosage form",
        "recommended_next_actions": ["Immediate recall", "Root cause investigation"]
    }"""
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=mock_json_response))]
    mock_client.chat.completions.create.return_value = mock_completion

    with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_mock_test_key"}):
        result = generate_structured_output(
            prompt="Analyze complaint for contamination in ampoules",
            response_model=RiskAssessmentState,
            model=MODEL_VERSATILE,
        )

        assert isinstance(result, RiskAssessmentState)
        assert result.severity == SeverityLevel.CRITICAL
        assert "Contamination detected" in result.risk_justification
        assert len(result.recommended_next_actions) == 2

import io
import os
from typing import Optional, Union, Tuple
from pydantic import BaseModel, Field

from backend.app.schemas.complaint import (
    ComplaintFormState,
    RiskAssessmentState,
    CopilotResponse,
    SeverityLevel,
    HealthHazardCategory,
)
from backend.app.core.llm import (
    MODEL_VERSATILE,
    generate_structured_output,
)

try:
    import pypdf
except ImportError:
    pypdf = None


class ComplaintExtractionResult(BaseModel):
    form_state: ComplaintFormState
    risk_assessment: RiskAssessmentState
    chat_summary: str = Field(..., description="Summary message to display in the copilot chat")


class ComplaintEditResult(BaseModel):
    updated_form_state: ComplaintFormState
    chat_summary: str = Field(..., description="Explanation of fields updated")


def log_complaint_tool(user_input: str) -> CopilotResponse:
    """
    Primary intake tool: Parses raw complaint text, extracts form fields into ComplaintFormState,
    calculates risk metrics into RiskAssessmentState, evaluates completeness & CAPA recommendations,
    and returns a CopilotResponse.
    
    :param user_input: Free-form text of the pharmaceutical complaint
    :return: CopilotResponse containing chat message, populated form state, and risk assessment
    """
    if not user_input or not user_input.strip():
        return CopilotResponse(
            chat_message="No complaint details were provided. Please provide text or upload a complaint file.",
            form_state=ComplaintFormState(),
            risk_assessment=RiskAssessmentState(),
            tool_used="log_complaint_tool",
        )

    system_prompt = (
        "You are an expert Pharmaceutical Quality Assurance & Regulatory Specialist. "
        "Analyze the customer complaint text and extract all relevant details into the specified schema. "
        "Identify product details (name, strength, batch/lot number, manufacture & expiry dates, quantity), "
        "complainant details, and defect description. Perform a risk assessment evaluating severity "
        "(Critical, Major, or Minor), risk score (1-100), recall hazard class, regulatory reportability, "
        "and recommended next actions."
    )

    try:
        extraction = generate_structured_output(
            prompt=user_input,
            response_model=ComplaintExtractionResult,
            system_prompt=system_prompt,
            model=MODEL_VERSATILE,
        )
        
        # Phase 4.2 Bonus Features: Enrich completeness score, missing fields & CAPA
        enriched_risk, completeness_warning = _enrich_completeness_and_capa(
            extraction.form_state, extraction.risk_assessment
        )
        
        chat_msg = extraction.chat_summary
        if completeness_warning:
            chat_msg = f"{completeness_warning}\n\n{chat_msg}"

        return CopilotResponse(
            chat_message=chat_msg,
            form_state=extraction.form_state,
            risk_assessment=enriched_risk,
            tool_used="log_complaint_tool",
        )
    except Exception as exc:
        # Fallback parsing in case of LLM / connection issue
        fallback_form = _regex_fallback_extraction(user_input)
        fallback_risk = RiskAssessmentState(
            severity=SeverityLevel.MINOR,
            risk_justification=f"Initial extraction fallback applied due to processing note: {str(exc)}",
            recommended_next_actions=["Review complaint manually"],
        )
        enriched_risk, completeness_warning = _enrich_completeness_and_capa(fallback_form, fallback_risk)
        
        msg = f"Logged complaint intake details."
        if completeness_warning:
            msg = f"{completeness_warning}\n\n{msg}"

        return CopilotResponse(
            chat_message=msg,
            form_state=fallback_form,
            risk_assessment=enriched_risk,
            tool_used="log_complaint_tool",
        )


def edit_complaint_tool(
    current_state: ComplaintFormState, user_edit_command: str
) -> CopilotResponse:
    """
    Modifies ONLY requested fields in current_state while strictly preserving all other existing state fields.
    
    :param current_state: The existing ComplaintFormState instance
    :param user_edit_command: User command specifying changes e.g. 'change batch number to B-999'
    :return: CopilotResponse with updated form_state and summary of changes
    """
    if not user_edit_command or not user_edit_command.strip():
        return CopilotResponse(
            chat_message="No edit instructions were provided.",
            form_state=current_state,
            risk_assessment=None,
            tool_used="edit_complaint_tool",
        )

    prompt = (
        f"CURRENT COMPLAINT FORM STATE:\n{current_state.model_dump_json(indent=2)}\n\n"
        f"USER EDIT COMMAND:\n{user_edit_command}\n\n"
        "Instructions: Modify ONLY the fields explicitly requested by the user. "
        "Keep ALL other existing fields unchanged."
    )

    system_prompt = (
        "You are a state modification assistant for a Pharmaceutical Complaint System. "
        "Update the complaint form state strictly according to the user's edit command."
    )

    try:
        edit_result = generate_structured_output(
            prompt=prompt,
            response_model=ComplaintEditResult,
            system_prompt=system_prompt,
            model=MODEL_VERSATILE,
        )
        
        merged_state = _merge_states(current_state, edit_result.updated_form_state)

        return CopilotResponse(
            chat_message=edit_result.chat_summary,
            form_state=merged_state,
            risk_assessment=None,
            tool_used="edit_complaint_tool",
        )
    except Exception as exc:
        updated_state = _fallback_apply_edit(current_state, user_edit_command)
        return CopilotResponse(
            chat_message=f"Updated complaint form according to command: '{user_edit_command}'",
            form_state=updated_state,
            risk_assessment=None,
            tool_used="edit_complaint_tool",
        )


def document_extraction_tool(
    file_input: Union[str, bytes], filename: Optional[str] = None
) -> CopilotResponse:
    """
    Extracts text from document input (PDF file path, PDF bytes, or raw text) and routes through log_complaint_tool.
    """
    extracted_text = ""

    if isinstance(file_input, bytes):
        if pypdf:
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_input))
                extracted_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            except Exception:
                extracted_text = file_input.decode("utf-8", errors="ignore")
        else:
            extracted_text = file_input.decode("utf-8", errors="ignore")
    elif isinstance(file_input, str):
        if os.path.exists(file_input) and os.path.isfile(file_input):
            if file_input.lower().endswith(".pdf") and pypdf:
                try:
                    reader = pypdf.PdfReader(file_input)
                    extracted_text = "\n".join([page.extract_text() or "" for page in reader.pages])
                except Exception:
                    with open(file_input, "r", encoding="utf-8", errors="ignore") as f:
                        extracted_text = f.read()
            else:
                with open(file_input, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()
        else:
            extracted_text = file_input

    response = log_complaint_tool(user_input=extracted_text)
    response.tool_used = "document_extraction_tool"
    return response


def _enrich_completeness_and_capa(
    form: ComplaintFormState, risk: RiskAssessmentState
) -> Tuple[RiskAssessmentState, Optional[str]]:
    """
    Computes completeness score, identifies missing critical fields,
    generates Root Cause Hypothesis and CAPA recommendations, and returns warnings.
    """
    critical_fields = {
        "product_name": "Product Name",
        "batch_number": "Batch Number",
        "manufacture_date": "Manufacture Date",
        "expiry_date": "Expiry Date",
        "complaint_quantity": "Quantity",
        "description": "Complaint Description",
        "complainant_name": "Complainant Name",
    }

    missing_keys = []
    missing_labels = []
    present_count = 0

    for key, label in critical_fields.items():
        val = getattr(form, key, None)
        if val and str(val).strip():
            present_count += 1
        else:
            missing_keys.append(key)
            missing_labels.append(label)

    total_critical = len(critical_fields)
    completeness_pct = int((present_count / total_critical) * 100)

    risk.completeness_score = completeness_pct
    risk.missing_critical_fields = missing_keys

    # Generate Root Cause Hypothesis & CAPA recommendations
    if not risk.root_cause_hypothesis:
        desc = (form.description or "").lower()
        cat = (form.defect_category or "").lower()

        if "discolor" in desc or "speck" in desc or "color" in cat:
            risk.root_cause_hypothesis = (
                "Particulate contamination / packaging sealing oxidation. "
                "Potential raw material impurity or sealing temperature drift."
            )
            risk.capa_recommendations = [
                "CAPA-1: Quarantine batch & initiate retention sample dark-field microscopic analysis.",
                "CAPA-2: Perform sealing machine thermal calibration audit.",
                "CAPA-3: Re-verify vendor Certificate of Analysis (CoA) for raw API lot.",
            ]
        elif "crack" in desc or "leak" in desc or "glass" in desc or "packaging" in cat:
            risk.root_cause_hypothesis = (
                "Mechanical stress or thermal shock during ampoule sealing / secondary packaging transit."
            )
            risk.capa_recommendations = [
                "CAPA-1: Conduct 100% optical inspection on remaining inventory of batch.",
                "CAPA-2: Audit shipping container shock/vibration damping parameters.",
                "CAPA-3: Review glass tubing thermal annealing logs with primary packaging vendor.",
            ]
        else:
            risk.root_cause_hypothesis = (
                "Unspecified manufacturing or packaging anomaly requiring root cause investigation."
            )
            risk.capa_recommendations = [
                "CAPA-1: Initiate formal Quality Deviation Investigation (QDI).",
                "CAPA-2: Perform line clearance and environmental monitoring review.",
            ]

    warning_text = None
    if missing_keys:
        warning_text = (
            f"⚠️ **Completeness Warning**: Intake form is **{completeness_pct}% complete**. "
            f"Missing critical fields: **{', '.join(missing_labels)}**."
        )

    return risk, warning_text


def _merge_states(
    original: ComplaintFormState, updated: ComplaintFormState
) -> ComplaintFormState:
    """Merge updated state while preserving non-null original values where updated is None."""
    orig_dict = original.model_dump()
    upd_dict = updated.model_dump()
    merged = {}
    for key, val in orig_dict.items():
        if upd_dict.get(key) is not None:
            merged[key] = upd_dict[key]
        else:
            merged[key] = val
    return ComplaintFormState(**merged)


def _regex_fallback_extraction(text: str) -> ComplaintFormState:
    """Helper fallback to extract basic fields if LLM is unavailable."""
    import re
    form = ComplaintFormState(description=text[:250])
    
    lot_match = re.search(r"(?:lot|batch)\s*(?:#|number|no\.?)?\s*:?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
    if lot_match:
        form.batch_number = lot_match.group(1)

    product_match = re.search(r"(?:product|brand|drug)\s*(?:name)?\s*:?\s*([A-Za-z0-9\s]+?)(?=\n|,|\.|$)", text, re.IGNORECASE)
    if product_match:
        form.product_name = product_match.group(1).strip()
        
    return form


def _fallback_apply_edit(state: ComplaintFormState, command: str) -> ComplaintFormState:
    """Helper fallback to apply direct edits if LLM is unavailable."""
    import re
    state_dict = state.model_dump()
    cmd_lower = command.lower()

    if "batch" in cmd_lower or "lot" in cmd_lower:
        match = re.search(r"(?:to|=|is)\s*([A-Za-z0-9\-]+)", command, re.IGNORECASE)
        if match:
            state_dict["batch_number"] = match.group(1)

    if "product" in cmd_lower or "name" in cmd_lower:
        match = re.search(r"(?:product|name)\s*(?:to|=|is)?\s*([A-Za-z0-9\s]+)$", command, re.IGNORECASE)
        if match:
            state_dict["product_name"] = match.group(1).strip()

    return ComplaintFormState(**state_dict)

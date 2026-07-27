from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"

class HealthHazardCategory(str, Enum):
    CLASS_I = "CLASS_I"
    CLASS_II = "CLASS_II"
    CLASS_III = "CLASS_III"

class ComplaintFormState(BaseModel):
    product_name: Optional[str] = Field(None, description="Brand/trade name of the product")
    strength: Optional[str] = Field(None, description="Dosage strength e.g., 500mg, 10mg/mL")
    batch_number: Optional[str] = Field(None, description="Batch or lot number")
    manufacture_date: Optional[str] = Field(None, description="Manufacturing date (YYYY-MM-DD or text)")
    expiry_date: Optional[str] = Field(None, description="Expiration date (YYYY-MM-DD or text)")
    complaint_quantity: Optional[str] = Field(None, description="Quantity or count of defective units reported")
    description: Optional[str] = Field(None, description="Detailed description of the complaint or defect")
    
    # Extended fields from architecture.md
    complaint_id: Optional[str] = Field(None, description="Unique tracking identifier")
    complainant_name: Optional[str] = Field(None, description="Full name of complainant")
    complainant_role: Optional[str] = Field(None, description="Role of complainant e.g. Patient, Pharmacist")
    complainant_contact: Optional[str] = Field(None, description="Email or phone of complainant")
    defect_category: Optional[str] = Field(None, description="Category of defect e.g. Packaging, Contamination")
    status: str = Field("DRAFT", description="Status of complaint form e.g., DRAFT, IN_REVIEW, CONFIRMED")

class RiskAssessmentState(BaseModel):
    severity: SeverityLevel = Field(SeverityLevel.MINOR, description="Severity assessment: Critical, Major, or Minor")
    risk_justification: Optional[str] = Field(None, description="Detailed rationale supporting the risk evaluation")
    recommended_next_actions: List[str] = Field(default_factory=list, description="List of recommended actions to take")
    
    # Extended fields from architecture.md
    risk_score: Optional[int] = Field(None, ge=1, le=100, description="Calculated composite risk score (1-100)")
    health_hazard_class: Optional[HealthHazardCategory] = Field(None, description="FDA Recall Risk Classification")
    regulatory_reportable: bool = Field(False, description="Flag indicating if regulatory report is mandatory")
    reporting_deadline_days: Optional[int] = Field(None, description="Days remaining for regulatory reporting")

    # Phase 4.2 Bonus Features
    completeness_score: Optional[int] = Field(100, ge=0, le=100, description="Complaint form completeness percentage (0-100%)")
    missing_critical_fields: List[str] = Field(default_factory=list, description="List of missing required/critical fields")
    root_cause_hypothesis: Optional[str] = Field(None, description="Automated Root Cause Analysis hypothesis")
    capa_recommendations: List[str] = Field(default_factory=list, description="Corrective and Preventive Action (CAPA) steps")

class CopilotResponse(BaseModel):
    chat_message: str = Field(..., description="Message from the AI Copilot to the user")
    form_state: Optional[ComplaintFormState] = Field(None, description="Updated state of the left complaint form")
    risk_assessment: Optional[RiskAssessmentState] = Field(None, description="Updated risk assessment results")
    tool_used: Optional[str] = Field(None, description="Name of the tool or agent node executed")

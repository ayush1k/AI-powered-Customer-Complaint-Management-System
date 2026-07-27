from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    JSON,
)
from backend.app.db.session import Base
from backend.app.schemas.complaint import (
    ComplaintFormState,
    RiskAssessmentState,
    SeverityLevel,
    HealthHazardCategory,
)


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(String(100), unique=True, index=True, nullable=True)
    
    # Product identification fields
    product_name = Column(String(255), nullable=True)
    strength = Column(String(100), nullable=True)
    batch_number = Column(String(100), index=True, nullable=True)
    manufacture_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    complaint_quantity = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # Complainant details
    complainant_name = Column(String(255), nullable=True)
    complainant_role = Column(String(100), nullable=True)
    complainant_contact = Column(String(255), nullable=True)
    defect_category = Column(String(100), nullable=True)
    status = Column(String(50), default="DRAFT")

    # Risk Assessment fields
    severity = Column(String(50), nullable=True)
    risk_justification = Column(Text, nullable=True)
    recommended_actions = Column(JSON, default=list)
    risk_score = Column(Integer, nullable=True)
    health_hazard_class = Column(String(50), nullable=True)
    regulatory_reportable = Column(Boolean, default=False)
    reporting_deadline_days = Column(Integer, nullable=True)

    # Phase 4.2 Bonus Features
    completeness_score = Column(Integer, default=100)
    missing_critical_fields = Column(JSON, default=list)
    root_cause_hypothesis = Column(Text, nullable=True)
    capa_recommendations = Column(JSON, default=list)

    # Metadata timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_form_state(self) -> ComplaintFormState:
        """Convert database record to ComplaintFormState Pydantic model."""
        return ComplaintFormState(
            complaint_id=self.complaint_id or f"CMP-{self.id}",
            product_name=self.product_name,
            strength=self.strength,
            batch_number=self.batch_number,
            manufacture_date=self.manufacture_date,
            expiry_date=self.expiry_date,
            complaint_quantity=self.complaint_quantity,
            description=self.description,
            complainant_name=self.complainant_name,
            complainant_role=self.complainant_role,
            complainant_contact=self.complainant_contact,
            defect_category=self.defect_category,
            status=self.status or "DRAFT",
        )

    def to_risk_state(self) -> RiskAssessmentState:
        """Convert database record to RiskAssessmentState Pydantic model."""
        sev = None
        if self.severity:
            try:
                sev = SeverityLevel(self.severity)
            except ValueError:
                sev = SeverityLevel.MINOR

        hazard = None
        if self.health_hazard_class:
            try:
                hazard = HealthHazardCategory(self.health_hazard_class)
            except ValueError:
                hazard = None

        return RiskAssessmentState(
            severity=sev or SeverityLevel.MINOR,
            risk_justification=self.risk_justification,
            recommended_next_actions=self.recommended_actions or [],
            risk_score=self.risk_score,
            health_hazard_class=hazard,
            regulatory_reportable=self.regulatory_reportable or False,
            reporting_deadline_days=self.reporting_deadline_days,
            completeness_score=self.completeness_score if self.completeness_score is not None else 100,
            missing_critical_fields=self.missing_critical_fields or [],
            root_cause_hypothesis=self.root_cause_hypothesis,
            capa_recommendations=self.capa_recommendations or [],
        )

    @classmethod
    def from_states(
        cls,
        form: ComplaintFormState,
        risk: RiskAssessmentState = None,
        complaint_id: str = None,
    ):
        """Construct a Complaint model instance from Pydantic form and risk states."""
        actions = risk.recommended_next_actions if risk else []
        sev_str = risk.severity.value if risk and risk.severity else None
        hazard_str = (
            risk.health_hazard_class.value if risk and risk.health_hazard_class else None
        )

        return cls(
            complaint_id=complaint_id or form.complaint_id,
            product_name=form.product_name,
            strength=form.strength,
            batch_number=form.batch_number,
            manufacture_date=form.manufacture_date,
            expiry_date=form.expiry_date,
            complaint_quantity=form.complaint_quantity,
            description=form.description,
            complainant_name=form.complainant_name,
            complainant_role=form.complainant_role,
            complainant_contact=form.complainant_contact,
            defect_category=form.defect_category,
            status=form.status or "DRAFT",
            severity=sev_str,
            risk_justification=risk.risk_justification if risk else None,
            recommended_actions=actions,
            risk_score=risk.risk_score if risk else None,
            health_hazard_class=hazard_str,
            regulatory_reportable=risk.regulatory_reportable if risk else False,
            reporting_deadline_days=risk.reporting_deadline_days if risk else None,
            completeness_score=risk.completeness_score if risk else 100,
            missing_critical_fields=risk.missing_critical_fields if risk else [],
            root_cause_hypothesis=risk.root_cause_hypothesis if risk else None,
            capa_recommendations=risk.capa_recommendations if risk else [],
        )

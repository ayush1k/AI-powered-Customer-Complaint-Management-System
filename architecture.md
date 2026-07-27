# System Architecture Document

## 1. Overview & Vision
The **AI-powered Customer Complaint Management System (AIVOA)** is an enterprise pharmaceutical complaint intake, processing, and risk assessment platform. It accelerates pharmaceutical product quality event resolution by automating document intake, multi-agent classification, regulatory risk scoring, and structured form auto-population.

---

## 2. Mandatory Tech Stack

| Component | Technology / Library | Purpose & Rationale |
| :--- | :--- | :--- |
| **Frontend Framework** | React (v18+) | Component-based UI architecture |
| **State Management** | Redux Toolkit | Centralized state management for left-panel form and right-panel copilot synchronization |
| **UI Design System** | Vanilla CSS + Inter Font | Clean enterprise styling, responsive layout, modern aesthetics |
| **Backend Framework** | Python 3.11+ / FastAPI | Asynchronous high-performance REST APIs & SSE streaming |
| **AI Orchestration** | LangGraph | Stateful multi-agent workflow routing, human-in-the-loop, and memory |
| **LLM Inference Provider**| Groq API (`gemma2-9b-it` & `llama-3.3-70b-versatile`) | Fast, low-latency LLM inference for classification, extraction & risk assessment |
| **Database & ORM** | PostgreSQL / MySQL + SQLAlchemy | Relational storage for complaint history, audit logs, and risk assessments |
| **Typography** | Inter Font | Modern, readable UI typography |

---

## 3. Core System Workflow & UI Architecture

### Dual-Panel Reactive Synchronized Architecture
```
+--------------------------------------------------+--------------------------------------------------+
|               LEFT PANEL (Reactive Form)          |           RIGHT PANEL (AIVOA Copilot Chat)       |
|                                                  |                                                  |
|  - Auto-populated & Read-only Form Fields        |  - Interactive Chat Interface                    |
|  - Complainant & Product Metadata                |  - File Upload (PDFs / Emails / Images)          |
|  - Defect Categorization                         |  - Real-time Agent Reasoning Logs                |
|  - Calculated Risk & Hazard Metrics              |  - Human-in-the-loop Confirmations & Overrides   |
|                                                  |                                                  |
+--------------------------------------------------+--------------------------------------------------+
                                        ^                                   |
                                        |--- Redux State Sync / Updates ----|
```

1. **Document Upload / Message Trigger**: User uploads a pharmaceutical complaint email or PDF via the Copilot Chat.
2. **LangGraph Agent Execution**: The backend executes a stateful graph powered by Groq LLMs (`gemma2-9b-it` for speed/extraction, `llama-3.3-70b-versatile` for complex risk analysis and reasoning).
3. **Structured Extraction**: Extracted fields (complainant information, drug details, lot numbers, event description, risk score) are returned via standardized API contracts.
4. **Redux State Synchronization**: The frontend receives the agent output and dispatches actions to update the Redux store, instantly updating the Left Reactive Form in real-time.

---

## 4. Data Models & Pydantic State Definitions

### 4.1 Complaint Form State (`ComplaintFormState`)
```python
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ProductDetails(BaseModel):
    product_name: Optional[str] = Field(None, description="Trade or brand name of the drug/device")
    generic_name: Optional[str] = Field(None, description="Active pharmaceutical ingredient (API)")
    dosage_form: Optional[str] = Field(None, description="Tablet, Injection, Solution, etc.")
    strength: Optional[str] = Field(None, description="Concentration e.g. 500mg, 10mg/mL")
    lot_number: Optional[str] = Field(None, description="Batch or lot identification number")
    expiration_date: Optional[str] = Field(None, description="YYYY-MM-DD or formatted expiration date")
    ndc_number: Optional[str] = Field(None, description="National Drug Code if available")

class ComplainantInfo(BaseModel):
    name: Optional[str] = Field(None, description="Full name of complainant")
    role: Optional[str] = Field(None, description="Patient, Physician, Pharmacist, Distributor, etc.")
    contact_email: Optional[str] = Field(None, description="Contact email address")
    contact_phone: Optional[str] = Field(None, description="Contact phone number")
    facility_name: Optional[str] = Field(None, description="Hospital or Pharmacy name")

class DefectInformation(BaseModel):
    category: Optional[str] = Field(None, description="Packaging, Contamination, Potency, Labeling, Adverse Event")
    description: Optional[str] = Field(None, description="Detailed text of reported complaint/defect")
    sample_received: bool = Field(False, description="Whether physical sample was received for testing")
    adverse_event_reported: bool = Field(False, description="Whether patient harm or AE occurred")

class ComplaintFormState(BaseModel):
    complaint_id: Optional[str] = Field(None, description="Unique tracking ID")
    complainant: ComplainantInfo = Field(default_factory=ComplainantInfo)
    product: ProductDetails = Field(default_factory=ProductDetails)
    defect: DefectInformation = Field(default_factory=DefectInformation)
    status: str = Field("DRAFT", description="Form status e.g., DRAFT, IN_REVIEW, CONFIRMED, SUBMITTED")
```

### 4.2 Risk Assessment State (`RiskAssessmentState`)
```python
class HealthHazardCategory(str, Enum):
    CLASS_I = "CLASS_I"    # Dangerous or defective products that predictably cause serious health consequences or death
    CLASS_II = "CLASS_II"  # Products that may cause temporary or medically reversible adverse health consequences
    CLASS_III = "CLASS_III"# Products not likely to cause adverse health consequences

class RiskAssessmentState(BaseModel):
    risk_score: Optional[int] = Field(None, ge=1, le=100, description="Calculated composite risk score (1-100)")
    severity: Optional[SeverityLevel] = Field(None, description="Assessed severity level")
    health_hazard_class: Optional[HealthHazardCategory] = Field(None, description="FDA Recall Risk Classification")
    regulatory_reportable: bool = Field(False, description="Flag indicating if FDA 15-day / MedWatch report is mandatory")
    reporting_deadline_days: Optional[int] = Field(None, description="Days remaining to report (e.g. 15 or 30 days)")
    justification: Optional[str] = Field(None, description="Detailed rationale supporting the risk evaluation")
    recommended_actions: List[str] = Field(default_factory=list, description="Immediate corrective actions or escalation steps")
```

---

## 5. API Endpoint Contracts

### 5.1 `POST /api/copilot/upload`
Uploads pharmaceutical complaint files (PDF, email MSG/EML, or images) for parsing and text extraction.

- **Request Headers**: `Content-Type: multipart/form-data`
- **Request Body**:
  - `file`: Binary file upload (`.pdf`, `.txt`, `.eml`, `.png`, `.jpg`)
  - `session_id` (optional): `string` - Existing conversation session ID
- **Response `200 OK`**:
```json
{
  "file_id": "file_892f3a",
  "filename": "complaint_lot_9921A.pdf",
  "content_type": "application/pdf",
  "raw_text": "Sample raw extracted text from document...",
  "session_id": "sess_10293847"
}
```
- **Errors**: `400 Bad Request` (unsupported format), `500 Internal Server Error`.

---

### 5.2 `POST /api/copilot/process`
Processes user prompts and uploaded documents through the LangGraph AI workflow, returning updated complaint state and copilot responses.

- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "session_id": "sess_10293847",
  "message": "Process uploaded complaint file file_892f3a and populate the form",
  "file_id": "file_892f3a",
  "current_form_state": {},
  "current_risk_state": {}
}
```
- **Response `200 OK`**:
```json
{
  "session_id": "sess_10293847",
  "agent_response": "Extracted complaint details for product Pharma Tablet 500mg (Lot #9921A). Risk score is calculated at 78 (High). Regulatory report required within 15 days.",
  "form_state": {
    "complaint_id": "CMP-2026-0042",
    "complainant": {
      "name": "Dr. Sarah Jenkins",
      "role": "Pharmacist",
      "contact_email": "s.jenkins@stjudehospital.org",
      "contact_phone": "+1-555-019-2831",
      "facility_name": "St. Jude Hospital Pharmacy"
    },
    "product": {
      "product_name": "CardioShield",
      "generic_name": "Enalapril Maleate",
      "dosage_form": "Tablet",
      "strength": "10mg",
      "lot_number": "LOT-9921A",
      "expiration_date": "2027-11-30",
      "ndc_number": "0006-0074-31"
    },
    "defect": {
      "category": "Contamination / Discoloration",
      "description": "Black specks observed inside sealed blister foil. Patient experienced mild nausea.",
      "sample_received": true,
      "adverse_event_reported": true
    },
    "status": "IN_REVIEW"
  },
  "risk_state": {
    "risk_score": 78,
    "severity": "HIGH",
    "health_hazard_class": "CLASS_II",
    "regulatory_reportable": true,
    "reporting_deadline_days": 15,
    "justification": "Particulate matter in oral tablets poses potential health risks; adverse event reported by hospital.",
    "recommended_actions": [
      "Quarantine lot LOT-9921A immediately",
      "File FDA 15-Day Alert Report",
      "Initiate retention sample inspection"
    ]
  }
}
```
- **Errors**: `422 Unprocessable Entity` (invalid payload), `500 Internal Server Error`.

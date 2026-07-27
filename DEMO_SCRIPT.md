# AIVOA - AI-Powered Customer Complaint Management System
## Video Presentation & Technical Demo Script (5-10 Minutes)

---

## 🎬 Video Overview & Timestamps

| Timestamp | Section | Key Focus Areas |
| :--- | :--- | :--- |
| **0:00 - 1:30** | **1. System Vision & Architecture** | Problem statement in Pharma QA, Dual-Panel UI, Tech Stack Overview |
| **1:30 - 4:30** | **2. Live End-to-End Demo** | PDF/Email Ingestion, Real-Time Form Auto-Population, State Preservation Edits, QMS Persistence |
| **4:30 - 7:30** | **3. Codebase Deep Dive** | LangGraph State Machine, Groq LLM Tools, Redux Dual-Panel Synchronization |
| **7:30 - 9:00** | **4. Bonus Features & Wrap Up** | Form Completeness Checker, AI Root Cause Analysis & CAPA Recommendations |

---

## 🏛️ Section 1: System Vision & Architecture Overview (1.5 Mins)

### Speaker Script:
> *"Hello everyone! Welcome to the demonstration of **AIVOA**, an enterprise AI-powered Customer Complaint Management System designed specifically for the pharmaceutical industry.*
>
> *In pharmaceutical quality assurance, intake processing for drug defects, packaging failures, and adverse event reports is historically slow, manual, and prone to human error. AIVOA solves this by combining multi-agent AI orchestration with a real-time reactive dual-panel interface.*
>
> *On the **Left Side**, we have a reactive Complaint Intake & Risk Assessment Form bound to Redux. On the **Right Side**, we have our interactive AIVOA Copilot powered by **Groq LLM inference** (`llama-3.3-70b-versatile` and `llama-3.1-8b-instant`) and **LangGraph state machines**.*
>
> *Let's jump into the live demo!"*

---

## ⚡ Section 2: Live End-to-End Demo Walkthrough (3 Mins)

### Step 1: Document Ingestion (PDF / Email)
1. **Action**: Click the **"Upload Complaint File"** button in the Copilot panel. Select `samples/complaint_letter_1.pdf` (or `samples/complaint_email_1.txt`).
2. **Narration**:
   > *"First, let's upload a formal pharmaceutical complaint letter (`complaint_letter_1.pdf`). Notice how the PDF is parsed instantly using `pypdf`, text is routed through our LangGraph document extraction tool, and the left-hand form populates in real-time."*
3. **Observed Output**:
   - **Product Name**: NeuroCalm Injection (5mg/mL)
   - **Batch / Lot Number**: BATCH-88402X
   - **Defect Description**: Hairline crack on ampoule neck
   - **AI Risk Assessment**: Severity **CRITICAL**, Risk Score **92/100**, Recall Hazard Class **CLASS_I**, FDA 15-Day Alert mandatory.

---

### Step 2: Natural Language Logging
1. **Action**: Type into Copilot input:
   > `"Log a complaint: Batch A123 of Paracetamol 500mg manufactured on Jan 2025 has discolored tablets."`
2. **Narration**:
   > *"Next, let's log a fresh complaint using free-form natural language. Our intent classifier routes this request to `log_complaint_tool`."*
3. **Observed Output**:
   - Form fields auto-populate: Product = Paracetamol, Strength = 500mg, Batch = A123, Mfg Date = Jan 2025.
   - Copilot chat confirms intake and provides risk rationale.

---

### Step 3: Selective Natural Language Editing & State Preservation
1. **Action**: Type into Copilot input:
   > `"Edit batch number to B-999"`
2. **Narration**:
   > *"Now, watch what happens when we issue a selective edit command. AIVOA updates ONLY the target field—Batch Number becomes `B-999`—while strictly preserving all other extracted product details, dates, and risk scores."*
3. **Observed Output**:
   - `batch_number` updates to `B-999`.
   - `product_name`, `strength`, `manufacture_date`, and `description` remain untouched.

---

### Step 4: QMS Database Persistence
1. **Action**: Click **"Submit to QMS Database"**.
2. **Narration**:
   > *"Once reviewed, clicking 'Submit to QMS Database' persists the full complaint form and risk metrics into our PostgreSQL/SQLite database via SQLAlchemy, generating an official tracking ID (`CMP-2026-0001`)."*

---

## 💻 Section 3: Codebase Deep Dive (3 Mins)

### 1. LangGraph Intent Router & Tool Nodes (`backend/app/agent/graph.py`)
- **Show Code**: Highlight `classify_intent_node` and `StateGraph` compilation:
```python
workflow.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "log_complaint": "log_complaint",
        "edit_complaint": "edit_complaint",
        "document_extraction": "document_extraction",
        "general_chat": "general_chat",
    }
)
```

### 2. Field Preservation Engine (`backend/app/agent/tools.py`)
- **Show Code**: Highlight `_merge_states` helper ensuring zero state drift:
```python
def _merge_states(original: ComplaintFormState, updated: ComplaintFormState) -> ComplaintFormState:
    orig_dict = original.model_dump()
    upd_dict = updated.model_dump()
    merged = {k: upd_dict[k] if upd_dict.get(k) is not None else v for k, v in orig_dict.items()}
    return ComplaintFormState(**merged)
```

### 3. Redux Dual-Panel Synchronization (`frontend/src/components/CopilotPanel.tsx`)
- **Show Code**: Highlight dual dispatch updating `chatSlice` and `formSlice` simultaneously:
```typescript
dispatch(addMessage({ sender: 'copilot', message: data.chat_message, tool_used: data.tool_used }));
dispatch(setEntireState({ formState: data.form_state, riskState: data.risk_assessment }));
```

---

## ⭐ Section 4: Bonus Features & Closing Remarks (1.5 Mins)

### Speaker Script:
> *"To complete our enterprise solution, we implemented three key bonus features:*
>
> 1. **Complaint Completeness Checker**: Automatically evaluates form fields, calculates a live 0-100% completeness score, lists missing critical fields, and displays a `Completeness Warning` header.
> 2. **Root Cause Analysis (AI-Inferred)**: Automatically analyzes defect narratives to generate root cause hypotheses (e.g. thermal stress during packaging transit).
> 3. **CAPA Recommendations**: Formulates structured Corrective & Preventive Action steps for quality managers.
>
> *Thank you for watching the AIVOA demonstration!"*

---

## 🧪 Verification & Execution Checklist

- [x] Backend running on `http://127.0.0.1:8000` (`uvicorn backend.app.main:app --reload`)
- [x] Frontend running on `http://localhost:3000` (`npm run dev` in `frontend/`)
- [x] Tested document uploads with [`samples/complaint_letter_1.pdf`](file:///workspaces/AI-powered-Customer-Complaint-Management-System/samples/complaint_letter_1.pdf) and [`samples/complaint_email_1.txt`](file:///workspaces/AI-powered-Customer-Complaint-Management-System/samples/complaint_email_1.txt).
- [x] Tested natural language intake & selective field edits.
- [x] Verified full 18-test suite green (`pytest`).

# AIVOA - AI-Powered Customer Complaint Management System 🏥⚡

> An enterprise pharmaceutical complaint intake, risk assessment, and QMS persistence platform powered by **FastAPI**, **LangGraph**, **Groq LLM Inference**, and **React + Redux Toolkit**.

---

## 📌 Project Overview

In pharmaceutical Quality Assurance (QA) and Regulatory Compliance, processing customer product complaints (e.g. drug defects, packaging integrity failures, or adverse health events) is traditionally manual, time-consuming, and error-prone. 

**AIVOA** revolutionizes complaint handling through an interactive, dual-panel AI Copilot interface:
- **Left Panel (Reactive Complaint & Risk Form)**: Auto-populates extracted product metadata, defect descriptions, and AI risk scores in real-time.
- **Right Panel (AIVOA Copilot Chat & Upload)**: Supports document ingestion (PDFs, text files, emails), natural language complaint logging, and selective field editing with **100% state preservation guarantee**.

---

## 🚀 Key Features & Architecture Highlights

```
+--------------------------------------------------+--------------------------------------------------+
|            LEFT PANEL: REACTIVE FORM             |         RIGHT PANEL: AIVOA COPILOT CHAT          |
|                                                  |                                                  |
|  - Read-only / Auto-populated Form Inputs        |  - Interactive Chat Interface                    |
|  - Complainant & Product Metadata                |  - File Upload Dropzone (PDFs / Emails)          |
|  - AI Risk Assessment & Recall Class Badge       |  - Real-time Agent Reasoning Badges              |
|  - Completeness Bar & CAPA Checklist             |  - Quick Prompt Shortcuts                        |
|  - "Submit to QMS Database" Button               |  - Natural Language Selective Field Edits        |
|                                                  |                                                  |
+--------------------------------------------------+--------------------------------------------------+
                                        ^                                   |
                                        |--- Redux Toolkit State Sync ------|
```

1. **Dual-Panel Redux Synchronization**: Form inputs and chat messages are bound to a unified Redux state (`formSlice` & `chatSlice`), delivering instant UI updates.
2. **LangGraph Agent Orchestration**: Stateful intent router classifies incoming requests (`log_complaint`, `edit_complaint`, `document_extraction`, `general_chat`) and executes specialized agent tools.
3. **Groq SDK Integration**: High-speed LLM inference using `llama-3.3-70b-versatile` (complex risk analysis) and `llama-3.1-8b-instant` (fast intent classification).
4. **Selective Editing with State Preservation**: Modifies ONLY the fields requested by the user (e.g., *"Edit batch number to B-999"*) while preserving all other extracted state fields intact.
5. **Bonus AI Features**:
   - **Form Completeness Checker**: Calculates a live 0–100% score, identifies missing critical fields, and emits warning alerts.
   - **Root Cause Hypothesis Analysis**: Infers underlying quality failure causes (e.g. thermal sealing drift, mechanical stress).
   - **CAPA Action Plan**: Formulates structured Corrective and Preventive Action (CAPA) steps.

---

## 🛠️ Tech Stack

| Layer | Technologies / Libraries |
| :--- | :--- |
| **Frontend UI** | React 18, Vite, TypeScript, Google Inter Font |
| **State Management** | Redux Toolkit (`@reduxjs/toolkit`), `react-redux` |
| **UI Components & Icons** | Vanilla CSS Tokens, Glassmorphism, `lucide-react` |
| **Backend API** | Python 3.11+, FastAPI, Uvicorn, `python-multipart` |
| **AI Orchestration** | LangGraph, LangChain Core |
| **LLM Inference Provider**| Groq API (`llama-3.3-70b-versatile` & `llama-3.1-8b-instant`) |
| **Database & ORM** | SQLAlchemy 2.0, SQLite / PostgreSQL (`psycopg2-binary`) |
| **Document Processing** | `pypdf`, `reportlab` |
| **Testing Suite** | `pytest`, `fastapi.testclient` (19 Automated Tests) |

---

## 📋 Prerequisites

Before running the application, ensure you have the following installed:
- **Python**: `v3.11` or higher
- **Node.js**: `v18.0` or higher (`npm` v9+)
- **Groq API Key**: Obtain a free API key from [console.groq.com](https://console.groq.com)

---

## ⚙️ Environment Variables Setup

Copy `.env.example` to `.env` in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```env
# Groq API Configuration
GROQ_API_KEY=gsk_your_actual_groq_api_key_here

# Database Configuration (Defaults to SQLite complaints.db if PostgreSQL is unavailable)
DATABASE_URL=sqlite:///./complaints.db
```

---

## 🐍 Backend Setup & Run Instructions

1. **Navigate to project root directory**:
   ```bash
   cd /path/to/AI-powered-Customer-Complaint-Management-System
   ```

2. **Create and activate a Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install backend dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Initialize database & seed sample records**:
   ```bash
   python backend/app/db/init_db.py
   ```

5. **Run the backend test suite**:
   ```bash
   pytest
   ```

6. **Start the FastAPI backend server**:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *The interactive Swagger API documentation will be available at `http://localhost:8000/docs`.*

---

## 💻 Frontend Setup & Run Instructions

1. **Open a new terminal and navigate to `frontend/`**:
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Verify production build (optional)**:
   ```bash
   npm run build
   ```

4. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   *Open your browser and navigate to `http://localhost:3000` (or `http://localhost:5173`).*

---

## 🧪 Usage & Testing Walkthrough Guide

### Scenario 1: Document Upload (PDF / Text Email)
1. Click **"Upload Complaint File"** in the Copilot panel.
2. Select [`samples/complaint_letter_1.pdf`](file:///workspaces/AI-powered-Customer-Complaint-Management-System/samples/complaint_letter_1.pdf) or [`samples/complaint_email_1.txt`](file:///workspaces/AI-powered-Customer-Complaint-Management-System/samples/complaint_email_1.txt).
3. **Result**: The left form auto-populates product name, lot number (`BATCH-88402X`), defect narrative, and AI risk score (`92/100` - Critical severity).

### Scenario 2: Free-Form Natural Language Intake
1. In the Copilot prompt bar, type:
   > `"Log a complaint: Batch A123 of Paracetamol 500mg manufactured on Jan 2025 has discolored tablets."`
2. Press **Send** or **Enter**.
3. **Result**: Form auto-fills Paracetamol 500mg details and displays AI Risk Assessment & CAPA steps.

### Scenario 3: Selective Natural Language Editing
1. In the Copilot prompt bar, type:
   > `"Edit batch number to B-999"`
2. Press **Send**.
3. **Result**: Batch number updates to `B-999` while product name, dosage, dates, and narrative remain strictly preserved.

### Scenario 4: Submit to QMS Database
1. Review the populated form on the left.
2. Click **"Submit to QMS Database"**.
3. **Result**: Record is saved to database, status updates to `SUBMITTED`, and tracking ID (`CMP-2026-0001`) is generated.

---

## 📂 Project Repository Sitemap

```
├── architecture.md             # System Architecture & API Contracts Document
├── DEMO_SCRIPT.md              # 5-10 Minute Video Walkthrough Script
├── memory.md                   # Project Progress & Verification Memory Log
├── .env.example                # Template Environment File
│
├── backend/
│   ├── requirements.txt        # Backend Python Dependencies
│   ├── test_cli_agent.py       # CLI Agent Test Runner
│   └── app/
│       ├── main.py             # FastAPI App Server & CORS Middleware
│       ├── api/                # REST API Endpoints (/copilot, /complaints)
│       ├── agent/              # LangGraph Workflow & Tool Definitions
│       ├── core/               # Groq LLM Client Wrapper
│       ├── db/                 # SQLAlchemy Models & Session Setup
│       └── schemas/            # Pydantic State Definitions
│
├── frontend/
│   ├── package.json            # Node.js Dependencies & Scripts
│   ├── vite.config.ts          # Vite Configuration & /api Proxy
│   ├── index.html              # HTML Entry Point with Inter Font
│   └── src/
│       ├── main.tsx            # React Root & Redux Provider
│       ├── App.tsx             # Main Dual-Panel Enterprise App Component
│       ├── index.css           # Global Design Tokens & Typography
│       ├── components/         # ComplaintForm & CopilotPanel Components
│       └── store/              # Redux Toolkit Slices (formSlice, chatSlice)
│
├── samples/                    # Sample Complaint Fixtures (.txt, .pdf)
├── scripts/                    # Utility Data Generator Scripts
└── tests/                      # 19 Automated Pytest Integration Suites
```

---

## 📄 License & Presentation

For a complete step-by-step video presentation guide, please refer to [`DEMO_SCRIPT.md`](file:///workspaces/AI-powered-Customer-Complaint-Management-System/DEMO_SCRIPT.md).
# MedCode AI – Clinical Documentation, Medical Coding & Claim Scrubbing Assistant

![MedCode AI Badge](https://img.shields.io/badge/Platform-MedCode_AI-06b6d4?style=for-the-badge&logo=medcode)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js_16-black?style=for-the-badge&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)

> **Regulatory & Clinical Safety Notice**: MedCode AI is an interactive prototype designed for demonstration and developer portfolio evaluation. AI suggestions for diagnostic (ICD-10-CM) and procedural (CPT) codes are strictly advisory recommendations that mandate certified human review (Physician / CPC / RHIA) before inclusion in official medical records or billing submissions.

---

## 🌟 Product Highlights & Architecture

MedCode AI streamlines the end-to-end medical administrative and revenue cycle pipeline:

```
[ Doctor-Patient Interaction ]
           │
           ▼
[ Live Session / Audio Stream ] ──▶ Progressive Speech-to-Text streaming & speaker turns
           │
           ▼
[ Clinical Information Extraction ] ─▶ Chief Complaint, Symptoms, Duration, History, SOAP
           │
           ▼
[ Medical Code Suggestions ] ─────▶ ICD-10-CM & CPT with Confidence & Evidence Rationale
           │
           ▼
[ Rule-Based Claim Scrubbing ] ───▶ Missing Docs, Duplicates, Mismatches & Compliance
           │
           ▼
[ Human Review Workspace ] ───────▶ Approve / Modify / Reject with Audit Trail
           │
           ▼
[ Dashboard Telemetry & Export ] ──▶ Aggregated pass rates, trend analytics, JSON export
```

---

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js (App Router), React 18/19, TypeScript
- **Styling**: Tailwind CSS (Dark theme, Glassmorphism cards, Neon-cyan & Indigo accents)
- **Icons & Visuals**: Lucide React
- **Analytics & Telemetry**: Recharts (Area charts, Donut diagrams, Bar charts)

### Backend
- **Framework**: Python 3.11+ with FastAPI & Pydantic v2
- **Database**: PostgreSQL 16 (with automatic zero-friction SQLite fallback for instant offline usage)
- **ORM**: SQLAlchemy 2.0
- **Security**: JWT tokens (PyJWT), password hashing (Bcrypt), CORS middleware

### Modular AI Service Layer
- **Out of the Box**: Pre-configured synthetic clinical models with multi-specialty cases (Cardiology, Endocrinology, Pulmonology, Orthopedics, Gastroenterology).
- **Zero Cost / Zero API Keys Required**: Works 100% locally for development, evaluation, and CI/CD.
- **Extensible Architecture**: Plug in Google Gemini 1.5, OpenAI GPT-4o, or Whisper STT with simple environment variable switches.

---

## 📁 Project Structure

```
medcode/
├── frontend/
│   ├── app/
│   │   ├── login/               # Authentication & one-click demo role login
│   │   ├── register/            # New clinical profile onboarding
│   │   ├── dashboard/           # KPIs, chart metrics, and recent encounters
│   │   ├── live/                # Simulated live streaming doctor-patient consultation
│   │   ├── transcripts/         # Searchable speech transcript repository
│   │   ├── clinical-notes/      # Extracted concepts, SOAP notes & AI disclaimers
│   │   ├── coding/              # ICD-10 & CPT recommendations with confidence
│   │   ├── scrubbing/           # 12-rule pre-bill claim scrubbing engine
│   │   ├── review/              # Human-in-the-loop review workspace & audit log
│   │   ├── history/             # Full historical timeline and JSON export
│   │   └── settings/            # AI model switcher & scrubbing rule toggles
│   ├── components/
│   │   ├── layout/              # Sidebar, Header, AppShell
│   │   └── ui/                  # MetricCard, GlassCard, StatusBadge, Modal, Toast
│   ├── lib/                     # API client, Auth context, Mock datasets, Utils
│   └── types/                   # Comprehensive TypeScript domain interfaces
│
├── backend/
│   ├── main.py                  # FastAPI application with CORS and lifespan hooks
│   ├── config.py                # Pydantic Settings and environment management
│   ├── database.py              # PostgreSQL engine with SQLite fallback
│   ├── models/                  # SQLAlchemy models (User, Session, Transcript, Note, Code, Scrub, Audit)
│   ├── schemas/                 # Pydantic request/response validation schemas
│   ├── routers/                 # REST API endpoints (/auth, /sessions, /coding, /scrubbing, etc.)
│   ├── services/
│   │   ├── ai_service.py        # Modular AI inference & rule-based engine
│   │   ├── auth_service.py      # JWT authentication and bcrypt hashing
│   │   └── seed_service.py      # Multi-specialty clinical demo dataset seeder
│   └── test_pipeline.py         # Automated end-to-end API test verification suite
│
├── docker-compose.yml           # PostgreSQL + FastAPI + Next.js orchestration
├── .env.example                 # Environment configuration template
└── README.md                    # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js v18+ & npm
- Python 3.10+

---

### Option 1: Running Locally (Recommended for Development)

#### 1. Start Backend
```bash
# From root directory:
pip install -r backend/requirements.txt

# Launch FastAPI on http://localhost:8000
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend will automatically create all database tables and seed realistic demo clinical cases on startup.*

#### 2. Start Frontend
```bash
# In a second terminal:
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

### Option 2: Running with Docker Compose

```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

---

## 🔑 Demo Credentials

For rapid prototype exploration, you can use the **One-Click Role Switcher** on the Login screen, or enter:

| Role | Email | Password |
|---|---|---|
| Attending Physician | `doctor@medcode.ai` | `demo123` |
| Certified Coder | `coder@medcode.ai` | `demo123` |
| Compliance Auditor | `auditor@medcode.ai` | `demo123` |

---

## 🔬 Core Clinical Demonstration Scenarios

1. **Cardiology**: 58 y/o male with exertional substernal chest discomfort (ICD-10: `R07.9`, `I10`, `E78.5` | CPT: `93000`, `99214`).
2. **Internal Medicine**: 64 y/o female with uncontrolled T2D and bilateral foot neuropathy (ICD-10: `E11.42`, `Z79.84` | CPT: `99214`).
3. **Pulmonology**: 34 y/o male with acute viral bronchitis and productive cough (ICD-10: `J20.9` | CPT: `99213`).

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | JWT login with password verification |
| `GET` | `/api/auth/me` | Current authenticated user profile |
| `GET` | `/api/dashboard/stats` | Aggregated telemetry & trend metrics |
| `GET` | `/api/sessions` | List all clinical patient encounters |
| `POST` | `/api/sessions` | Create a new clinical session |
| `POST` | `/api/transcripts` | Save audio speech transcript |
| `POST` | `/api/clinical-notes/analyze/{id}` | Extract structured concepts & SOAP note |
| `POST` | `/api/coding/analyze/{id}` | Generate ICD-10 and CPT recommendations |
| `POST` | `/api/scrubbing/run/{id}` | Run 12-rule claim scrubbing compliance checks |
| `GET` | `/api/reviews` | Retrieve review workspace and audit logs |
| `POST` | `/api/reviews/{id}/approve` | Approve code suggestion |
| `POST` | `/api/reviews/{id}/modify` | Override suggestion with custom code & reason |
| `POST` | `/api/reviews/{id}/reject` | Reject code with audit deficiency note |

---

## 🧪 Testing

Run the automated backend test suite:
```bash
python backend/test_pipeline.py
```
This tests all 13 core workflows from authentication through transcription, clinical notes, code generation, scrubbing, and reviewer audit trails.

# 🚀 IntelliHire Pro v2.0

> **AI-Powered Hiring Platform** — Resume Analysis · Interview Generation · Smart Evaluation

Built with **FastAPI + OpenAI + React + Recharts**. Fully modular, production-ready, beginner-friendly.

---

## ✨ Features

| Feature | Description |
|---|---|
| **AI Resume Analyzer** | Upload PDF/DOCX → extract skills, experience, education, domain, score (0–100) |
| **Job Fit Score** | Paste a job description → get a fit score, breakdown, strengths & gap analysis |
| **Interview Generator** | AI generates technical + behavioral questions by role, difficulty, and skills |
| **Smart Evaluator** | AI scores answers (0–10), gives feedback, strengths & improvement areas |
| **Dashboard** | View history, score distribution charts, stats |
| **Auth** | JWT-based register/login (optional — all core features work without login) |
| **Graceful Fallback** | Works without an OpenAI key using smart heuristics |

---

## 🏗️ Architecture

```
intellihire-pro/
├── backend/
│   ├── app/
│   │   ├── api/            # Route handlers
│   │   │   ├── auth_routes.py
│   │   │   ├── resume_routes.py
│   │   │   ├── interview_routes.py
│   │   │   └── admin_routes.py
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic v2 request/response schemas
│   │   ├── services/       # Business logic
│   │   │   ├── ai_service.py      # OpenAI integration + fallbacks
│   │   │   └── resume_service.py  # PDF/DOCX text extraction
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── security.py     # bcrypt + JWT
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ui/         # Design system components
    │   │   └── layout/     # Navbar
    │   ├── pages/          # Home, Resume, Interview, Dashboard, Auth
    │   ├── services/       # Axios API client
    │   ├── store/          # Zustand auth store
    │   └── App.jsx         # Router
    ├── package.json
    └── .env.example
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- An [OpenAI API key](https://platform.openai.com/api-keys) *(optional — fallback mode works without it)*

---

### 1. Clone / Unzip

```bash
unzip intellihire-pro.zip
cd intellihire-pro
```

---

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and set your OPENAI_API_KEY
```

**Edit `backend/.env`:**
```env
OPENAI_API_KEY=sk-...your-key-here...
OPENAI_MODEL=gpt-4o-mini
SECRET_KEY=change-this-to-a-random-string
DATABASE_URL=sqlite:///./intellihire.db
```

**Run the backend:**
```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: **http://localhost:8000**
Interactive docs at: **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional)
cp .env.example .env
# VITE_API_URL defaults to http://localhost:8000

# Run development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## 🔑 API Reference

All endpoints prefixed with `/api`.

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login → returns JWT token |
| GET  | `/api/auth/me` | Get current user (requires Bearer token) |

### Resume
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/resume/upload-resume` | Upload + analyze resume (form-data: `file`, optional `job_role`, `job_description`) |
| POST | `/api/resume/job-fit` | Compute job fit for existing analysis |
| GET  | `/api/resume/history` | Get analysis history (requires auth) |
| GET  | `/api/resume/{id}` | Get specific analysis |

### Interview
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/interview/generate-questions` | Generate AI questions |
| POST | `/api/interview/evaluate-answer` | Evaluate a candidate answer |
| POST | `/api/interview/save` | Save an interview record |
| GET  | `/api/interview/history` | Get interview history |
| DELETE | `/api/interview/{id}` | Delete an interview record |

---

## 📝 Example API Usage

### Upload & Analyze Resume

```bash
curl -X POST http://localhost:8000/api/resume/upload-resume \
  -F "file=@resume.pdf" \
  -F "job_role=Senior Backend Developer" \
  -F "job_description=We are looking for a Python expert with 5+ years..."
```

**Response:**
```json
{
  "id": 1,
  "filename": "resume.pdf",
  "candidate_name": "Jane Smith",
  "summary": "Experienced backend engineer with 6 years...",
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "experience_years": 6.0,
  "domain": "Backend",
  "resume_score": 82.0,
  "fit_score": 78.0,
  "fit_breakdown": { "skills_match": 32, "experience_match": 25, ... },
  "improvements": ["Add quantified achievements", "Include CI/CD experience"]
}
```

### Generate Interview Questions

```bash
curl -X POST http://localhost:8000/api/interview/generate-questions \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Data Scientist",
    "skills": ["Python", "scikit-learn", "SQL"],
    "difficulty": "mixed",
    "num_questions": 5,
    "include_behavioral": true
  }'
```

### Evaluate an Answer

```bash
curl -X POST http://localhost:8000/api/interview/evaluate-answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the difference between overfitting and underfitting.",
    "answer": "Overfitting is when a model learns the training data too well...",
    "role": "Data Scientist"
  }'
```

---

## 🚀 Production Deployment

### Backend (Gunicorn + PostgreSQL)

```bash
# Install gunicorn
pip install gunicorn

# Set production env vars
export DATABASE_URL=postgresql://user:pass@localhost:5432/intellihire
export SECRET_KEY=your-long-random-secret

# Run
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Build)

```bash
npm run build
# Serve the `dist/` folder with Nginx or any static host
```

### Docker (optional)

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔧 Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Your OpenAI key. Without it, heuristic fallback mode activates. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use. `gpt-4o` for highest quality. |
| `SECRET_KEY` | (insecure default) | **Change in production!** Used for JWT signing. |
| `DATABASE_URL` | `sqlite:///./intellihire.db` | Any SQLAlchemy-compatible URL. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT token lifetime (24h default). |
| `VITE_API_URL` | `http://localhost:8000` | Frontend → backend URL. |

---

## 🛠️ Tech Stack

**Backend:** FastAPI · SQLAlchemy · SQLite/PostgreSQL · OpenAI SDK · pdfplumber · python-docx · python-jose · passlib

**Frontend:** React 18 · React Router · Zustand · Axios · Recharts · Framer Motion · Lucide Icons · react-hot-toast

---

## 📄 License

MIT — free to use and modify.

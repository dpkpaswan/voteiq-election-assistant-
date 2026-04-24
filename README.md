<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" />
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" />
  <img src="https://img.shields.io/badge/Tests-121%20Passed-success?style=for-the-badge&logo=pytest" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

<h1 align="center">🧠 VoteIQ</h1>
<h3 align="center">Election Process Education Assistant 🇮🇳</h3>

<p align="center">
  <em>An AI-powered conversational assistant that helps Indian citizens understand<br>
  voter registration, election timelines, and voting steps — simply and clearly.</em>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-google-cloud-integration">Google Cloud</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-testing">Testing</a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **AI Chat** | Multi-turn conversational assistant powered by Google Gemini |
| 🧭 **Step Guides** | Step-by-step instructions for registration, voting, documents, polling, results |
| 📅 **Timeline** | Election timeline with phases, deadlines, and upcoming events |
| 🧠 **Intent Detection** | AI-powered classification of user queries (7 categories) |
| 🛡️ **Security** | Rate limiting, input sanitization, prompt injection protection |
| 📱 **Responsive UI** | Premium glassmorphism dark theme with Firebase Analytics |
| ☁️ **Google Cloud Native** | Gemini + Firestore + Cloud Logging + Secret Manager + GCS |
| 🔄 **100% Uptime** | Template-based fallback ensures the app works without an API key |

---

## ☁️ Google Cloud Integration

VoteIQ deeply integrates **6 Google Cloud services**:

```
┌──────────────────────────────────────────────────────────────┐
│                 🌐 GOOGLE CLOUD PLATFORM                     │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Google Gemini    │  │  Cloud Firestore  │                │
│  │  • Chat Sessions  │  │  • Chat History   │                │
│  │  • Intent Classif.│  │  • Analytics      │                │
│  │  • Embeddings     │  │  • User Feedback  │                │
│  │  • Safety Filters │  │  • Daily Metrics  │                │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Cloud Logging    │  │  Secret Manager   │                │
│  │  • Structured Logs│  │  • API Keys       │                │
│  │  • Request Metrics│  │  • Model Config   │                │
│  │  • Chat Analytics │  │  • Env Fallback   │                │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Cloud Storage    │  │  Firebase         │                │
│  │  • Knowledge Base │  │  • Analytics      │                │
│  │  • Election Data  │  │  • Performance    │                │
│  │  • Local Fallback │  │  • Hosting        │                │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Google Cloud Run (Serverless Deployment)             │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

| Service | Purpose | Fallback |
|---------|---------|----------|
| **Google Gemini AI** | Chat, intent classification, embeddings | Template responses |
| **Cloud Firestore** | Chat history, analytics, feedback | In-memory (stateless) |
| **Cloud Logging** | Structured logs, request metrics | Python `logging` |
| **Secret Manager** | Secure API key storage | Environment variables |
| **Cloud Storage** | Knowledge base files | Local `data/` directory |
| **Firebase Analytics** | User interaction tracking | Silent no-op |
| **Firebase Performance** | Page load & API latency monitoring | Silent no-op |
| **Firebase Hosting** | Frontend CDN deployment | Local dev server |
| **Google Cloud Run** | Backend container hosting | Local uvicorn |
| **Google Fonts** | Inter + Space Grotesk typography | System fonts |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│     HTML5 + CSS3 (Glassmorphism) + JavaScript (ES6+)        │
│     Firebase Analytics + Firebase Performance Monitoring     │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │ Onboarding │  │  Chat UI   │  │    Sidebar Panel       │ │
│  │   Splash   │→ │  Messages  │  │  • Quick Start         │ │
│  │            │  │  Typing    │  │  • Suggestions          │ │
│  └────────────┘  │  Input     │  │  • Sources              │ │
│                  └─────┬──────┘  └────────────────────────┘ │
│                        │ Fetch API                           │
└────────────────────────┼─────────────────────────────────────┘
                         │ HTTPS (JSON)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI + Google Cloud)               │
│                                                              │
│  ┌─────────┐   ┌──────────────┐   ┌──────────────────────┐ │
│  │  CORS   │   │ Rate Limiter │   │  Security Headers    │ │
│  │Middleware│   │  (30/min)    │   │  + Cloud Logging     │ │
│  └────┬────┘   └──────┬───────┘   └──────────┬───────────┘ │
│       └───────────────┬┘                      │             │
│                       ▼                       │             │
│  ┌────────────────────────────────────────────▼───────────┐ │
│  │                    API ROUTES                          │ │
│  │  POST /api/chat  │ GET /api/timeline │ GET /api/steps  │ │
│  └───────┬──────────┴────────┬──────────┴────────┬───────┘ │
│          ▼                   ▼                    ▼         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  Assistant   │  │  Timeline    │  │    Step           │ │
│  │  + Firestore │  │  Service     │  │    Service        │ │
│  │  + Logging   │  │              │  │                   │ │
│  └──────┬───────┘  └──────────────┘  └──────────────────┘ │
│         │                                                   │
│    ┌────┴────────────────┐                                 │
│    ▼                     ▼                                 │
│ ┌───────────┐   ┌──────────────┐                          │
│ │  Intent   │   │   Gemini     │──→ Google Gemini API     │
│ │  Service  │   │   Service    │    (Chat Sessions +      │
│ │ (AI+KW)   │   │  + Embeddings│     Safety Settings)     │
│ └───────────┘   └──────────────┘                          │
│                                                             │
│  ┌───────────┐  ┌───────────┐  ┌───────────────────────┐  │
│  │ Firestore │  │  Secret   │  │   Cloud Storage       │  │
│  │ (History) │  │  Manager  │  │   (Knowledge Base)    │  │
│  └───────────┘  └───────────┘  └───────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 How It Works

### Chat Flow

```
  User types question
        │
        ▼
  ┌─────────────────┐
  │  Input Validation│ ──✗──→ 400 Error
  │  & Sanitization  │        "Invalid input"
  └────────┬────────┘
           │ ✓
           ▼
  ┌─────────────────┐        ┌────────────────┐
  │ Intent Detection │──AI──→│ Gemini Classify │
  │                  │        │ (7 categories)  │
  │  confidence < 0.6│──KW──→│ Keyword Fallback│
  └────────┬────────┘        └────────────────┘
           │
           ▼
  ┌─────────────────┐
  │ Context Builder  │ ← India-specific data
  │ (ECI, NVSP, EVM) │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐        ┌────────────────┐
  │ Gemini Chat API  │──AI──→│ Multi-turn Chat │
  │                  │        │ (Session-based) │
  │  API unavailable │──FB──→│ Template Resp.  │
  └────────┬────────┘        └────────────────┘
           │
           ├──→ Cloud Firestore (save chat history)
           ├──→ Cloud Logging (log interaction metrics)
           │
           ▼
  ┌─────────────────┐
  │ JSON Response    │
  │ • response text  │
  │ • intent         │
  │ • suggestions    │
  │ • sources        │
  └─────────────────┘
```

---

## 📂 Project Structure

```
VoteIQ/
│
├── 📁 backend/                        # FastAPI + Google Cloud
│   ├── 📁 app/
│   │   ├── 📁 routes/                 # API endpoints
│   │   │   ├── chat.py                #   POST /api/chat
│   │   │   ├── timeline.py            #   GET  /api/timeline/*
│   │   │   └── steps.py               #   GET  /api/steps/*
│   │   ├── 📁 services/               # Business logic + GCP
│   │   │   ├── assistant_service.py   #   Main orchestrator
│   │   │   ├── gemini_service.py      #   Gemini AI (Chat + Embeddings)
│   │   │   ├── intent_service.py      #   Intent classification
│   │   │   ├── timeline_service.py    #   Timeline data
│   │   │   ├── step_service.py        #   Step-by-step guides
│   │   │   ├── firestore_service.py   #   ☁️ Cloud Firestore
│   │   │   ├── cloud_logging_service.py  # ☁️ Cloud Logging
│   │   │   ├── secret_manager_service.py # ☁️ Secret Manager
│   │   │   └── cloud_storage_service.py  # ☁️ Cloud Storage
│   │   ├── 📁 utils/
│   │   │   └── validators.py          #   Input sanitization
│   │   ├── 📁 data/
│   │   │   └── election_knowledge.json
│   │   ├── config.py                  # Config + Secret Manager
│   │   ├── main.py                    # Entry point
│   │   ├── models.py                  # Pydantic schemas
│   │   └── server.py                  # App factory + Cloud Logging
│   ├── 📁 tests/                      # 121 tests ✅
│   │   ├── test_api.py                #   30 API endpoint tests
│   │   ├── test_validators.py         #   28 security tests
│   │   ├── test_steps.py              #   14 step service tests
│   │   ├── test_google_services.py    #   39 Google Cloud tests
│   │   ├── test_timeline.py           #   5 timeline tests
│   │   ├── test_intent.py             #   4 intent tests
│   │   └── test_assistant.py          #   1 assistant test
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── 📁 frontend/                       # Premium dark-theme SPA
│   ├── index.html                     # HTML5 + Firebase SDK
│   ├── style.css                      # Glassmorphism design
│   ├── script.js                      # API + Firebase Analytics
│   └── README.md
│
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google API Key ([Get one here](https://makersuite.google.com/app/apikey))

### 1️⃣ Clone

```bash
git clone https://github.com/dpkpaswan/voteiq-election-assistant-.git
cd voteiq-election-assistant-
```

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

### 3️⃣ Configure Environment

```bash
copy .env.example .env
# Edit .env and add your Google API Key
```

```env
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-pro
GOOGLE_CLOUD_PROJECT=your-gcp-project
ENV=production
```

### 4️⃣ Run Backend

```bash
uvicorn app.main:app --reload
```

🔗 API: http://localhost:8000
📚 Docs: http://localhost:8000/docs

### 5️⃣ Run Frontend

```bash
cd ../frontend
python -m http.server 3000
```

🌐 Open: http://localhost:3000

---

## 📡 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | 💬 Chat with VoteIQ (multi-turn Gemini sessions) |
| `GET` | `/api/timeline` | 📅 Full election timeline |
| `GET` | `/api/timeline/upcoming` | ⏳ Upcoming election events |
| `GET` | `/api/timeline/deadlines` | 🔔 Election deadlines |
| `GET` | `/api/timeline/event/{name}` | 🔍 Search event by name |
| `GET` | `/api/steps` | 🧭 All step-by-step guides |
| `GET` | `/api/steps/{step_id}` | 📋 Specific step guide |
| `GET` | `/health` | ❤️ Health + Google Services status |
| `GET` | `/info` | 📊 App config + GCP services |

### Chat Request

```json
POST /api/chat
{
  "message": "How do I register to vote in India?",
  "session_id": "sess_1713800000000",
  "mode": "guide"
}
```

### Chat Response

```json
{
  "success": true,
  "data": {
    "response": "To vote in India, you must be registered...",
    "intent": "registration",
    "confidence": 0.85,
    "mode": "guide",
    "follow_up_suggestions": [
      "How do I check if I'm on the Electoral Roll?",
      "Can I apply for a Voter ID online?",
      "What documents are needed for registration?"
    ],
    "sources": [
      "Election Commission of India (eci.gov.in)",
      "National Voters' Service Portal (nvsp.in)",
      "Voter Helpline App"
    ]
  }
}
```

### Health Response (with Google Services)

```json
{
  "status": "ok",
  "app": "VoteIQ",
  "version": "2.1.0",
  "ai_enabled": true,
  "google_services": {
    "gemini_ai": true,
    "cloud_logging": true,
    "firestore": true,
    "cloud_storage": true,
    "secret_manager": false,
    "gcp_project": true
  }
}
```

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

```
====================== 121 passed in 59.64s =======================
```

### Test Coverage

| Test Suite | Tests | What It Covers |
|------------|:-----:|----------------|
| `test_google_services.py` | **39** | Cloud Logging, Firestore, Secret Manager, GCS, Gemini Sessions |
| `test_api.py` | 30 | All HTTP endpoints, error responses, security headers |
| `test_validators.py` | 28 | Input validation, sanitization, prompt injection, XSS |
| `test_steps.py` | 14 | Step guides, data quality, serialization |
| `test_timeline.py` | 5 | Timeline data, deadlines, event search |
| `test_intent.py` | 4 | Intent classification, keyword fallback |
| `test_assistant.py` | 1 | Assistant orchestration fallback |
| **Total** | **121** | **Full coverage across all services** |

---

## 🛡️ Security

| Protection | Implementation |
|------------|---------------|
| **Rate Limiting** | Sliding window — 30 req/60 sec per IP |
| **Input Validation** | Length, pattern rejection, character analysis |
| **Prompt Injection** | 17+ blocked patterns |
| **XSS Prevention** | HTML entity encoding |
| **Security Headers** | `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy` |
| **CORS** | Configurable allowed origins |
| **Secret Manager** | API keys secured via GCP Secret Manager |
| **Error Masking** | Internal errors never exposed |
| **Gemini Safety** | 4-category content filtering |
| **Non-root Docker** | Container runs as `appuser` |

---

## 🌟 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | **FastAPI** (Python) | REST API framework |
| AI/LLM | **Google Gemini** | Chat sessions + intent + embeddings |
| Database | **Cloud Firestore** | Chat history + analytics |
| Logging | **Cloud Logging** | Structured request metrics |
| Secrets | **Secret Manager** | Secure credential management |
| Storage | **Cloud Storage** | Knowledge base files |
| Frontend | **HTML5 + CSS3 + JS** | Premium glassmorphism SPA |
| Analytics | **Firebase Analytics** | User interaction tracking |
| Performance | **Firebase Performance** | Load time monitoring |
| Hosting | **Firebase Hosting** | CDN frontend deployment |
| Container | **Cloud Run** | Serverless backend |
| Typography | **Google Fonts** | Inter + Space Grotesk |
| Testing | **Pytest** | 121 tests |

---

## 🐳 Docker

```bash
cd backend
docker build -t voteiq .
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=your_key \
  -e GEMINI_MODEL=gemini-1.5-pro \
  -e GOOGLE_CLOUD_PROJECT=your-project \
  voteiq
```

---

## ☁️ Deployment

```bash
# Backend → Google Cloud Run
cd backend
gcloud run deploy voteiq-backend \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_API_KEY=key,ENV=production"

# Frontend → Firebase Hosting
cd frontend
firebase init hosting
firebase deploy
```

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Author

**Deepak Paswan** — Built for [PromptWars Challenge](https://github.com/dpkpaswan/voteiq-election-assistant-) 🚀

---

<p align="center">
  ⭐ <strong>Star this repo if you found it useful!</strong><br>
  <sub>Made with ❤️ for Indian democracy | Powered by Google Cloud</sub>
</p>
# 🧠 VoteIQ Backend — Election Process Education Assistant

FastAPI-powered backend API for VoteIQ.

## ⚙️ Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your Google API key

# Run server
uvicorn app.main:app --reload
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## 📡 API Endpoints

| Method | Endpoint                     | Description                      |
| ------ | ---------------------------- | -------------------------------- |
| POST   | `/api/chat`                  | Chat with VoteIQ assistant       |
| GET    | `/api/timeline`              | Full election timeline           |
| GET    | `/api/timeline/upcoming`     | Upcoming election events         |
| GET    | `/api/timeline/deadlines`    | Election deadlines               |
| GET    | `/api/timeline/event/{name}` | Search event by name             |
| GET    | `/api/steps`                 | All step-by-step guides          |
| GET    | `/api/steps/{step_id}`       | Specific step guide              |
| GET    | `/health`                    | Health check                     |
| GET    | `/info`                      | App info                         |

## 🧪 Tests

```bash
pytest tests/ -v
```

## 🐳 Docker

```bash
docker build -t voteiq-backend .
docker run -p 8080:8080 voteiq-backend
```

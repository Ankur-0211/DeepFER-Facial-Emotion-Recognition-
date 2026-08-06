# DeepFER

**Real-Time Facial Emotion Recognition Using Deep Learning**
Deep Learning for Computer Vision — Course Project

DeepFER detects faces in an uploaded photo, an uploaded video, or a live webcam stream, and classifies the displayed emotion — Angry, Disgust, Fear, Happy, Sad, Surprise, or Neutral — using a CNN trained on FER2013.

Full write-up: [`docs/DeepFER_Project_Documentation.md`](docs/DeepFER_Project_Documentation.md)
Design rationale: [`docs/DeepFER_Software_Design_Document.docx`](docs/DeepFER_Software_Design_Document.docx)

---

## Live Demo

- **App:** _add your Render frontend URL here_
- **API health check:** _add your Render backend URL here_`/health`
- **Demo video:** _add link here_

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, JWT auth, PostgreSQL, SQLAlchemy, Alembic |
| ML | TensorFlow/Keras (CNN), OpenCV (Haar Cascade) |
| Testing | PyTest, Jest + React Testing Library, Locust |
| Deployment | Docker, Render |

---

## Project Structure

```
deepfer/
├── backend/        # FastAPI service — auth, prediction endpoints, WebSocket stream
├── ml/             # Data preprocessing, CNN training, inference engine
├── frontend/        # React + TypeScript SPA
├── docker/           # Dockerfiles + nginx config
├── docker-compose.yml
└── docs/              # SDD, evaluation reports, full documentation
```

See [`docs/DeepFER_Explained_Simply.md`](docs/DeepFER_Explained_Simply.md) for a plain-language walkthrough of every folder and the full request flow.

---

## Running Locally

### Option A — Docker Compose (recommended, closest to production)

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Health check: http://localhost:8000/health

### Option B — Run each service manually

**Database**
```bash
docker compose up -d db
```

**Backend** (Python 3.12, own venv)
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend** (Node 18+)
```bash
cd frontend
npm install
npm run dev
```

Then: register → log in → use the NavBar to reach **Live Detect** → upload a photo, a video, or use the webcam → check **Dashboard** for aggregated results.

---

## Running Tests

**Backend**
```bash
cd backend
pytest -v
```

**ML pipeline**
```bash
cd ml
pytest -v
```

**Frontend**
```bash
cd frontend
npm test
```

**Load / performance testing**
```bash
cd backend
locust -f loadtests/locustfile.py --host http://127.0.0.1:8000     # REST latency
python loadtests/ws_fps_test.py                                     # WebSocket FPS
```
Backend must be running first. See `docs/DeepFER_Project_Documentation.md` §6 for recorded results and NFR comparisons.

---

## Model

- **Architecture:** 3-block CNN with Global Average Pooling
- **Dataset:** FER2013 (35,887 images, 7 classes)
- **Test accuracy:** 61.95%
- Full per-class metrics and training notes: `docs/DeepFER_Project_Documentation.md` §5, and `docs/model_evaluation_report.md`

---

## Environment Variables

| Variable | Used by | Purpose |
|---|---|---|
| `DATABASE_URL` | backend | PostgreSQL connection string |
| `JWT_SECRET_KEY` | backend | Signing key for auth tokens |
| `CORS_ORIGINS` | backend | Comma-separated list of allowed frontend origins |
| `VITE_API_BASE_URL` | frontend (build-time) | Backend URL the frontend calls |

Backend defaults are defined in `backend/app/core/config.py`; override via `backend/.env` locally or via environment variables on the deployment platform.

---

## API Overview

All endpoints versioned under `/api/v1`. Full interactive docs available at `/docs` on the running backend (FastAPI auto-generated OpenAPI/Swagger UI).

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Create account | No |
| POST | `/api/v1/auth/login` | Authenticate | No |
| POST | `/api/v1/predict/image` | Predict emotion from a single image | Yes |
| POST | `/api/v1/predict/video` | Predict emotion timeline from a video | Yes |
| WS | `/ws/v1/stream` | Live webcam emotion streaming | Yes |
| GET | `/api/v1/reports/summary` | Aggregated emotion analytics | Yes |
| GET | `/health` | Service health check | No |

---

## Known Limitations

- CPU-only inference; single dedicated inference thread by design (TensorFlow/Windows thread-safety). Webcam streaming achieves ~5 FPS against a 10 FPS target — GPU inference would close this gap.
- `fear` is the weakest predicted class (29% recall) — a well-documented hard case in FER2013 research generally.
- Deployed on Render (Docker + managed Postgres) rather than the SDD's originally specified AWS stack, for delivery-time efficiency.

Full details: `docs/DeepFER_Project_Documentation.md` §7.

# Zomato // AI Dining Concierge ✨

An advanced AI-powered restaurant recommendation and dining intelligence platform inspired by the minimalist design language of **Ultrahuman** and the rich culinary ecosystem of **Zomato**. The system integrates structured restaurant data ($12,151+$ restaurants across $93+$ Bangalore localities) with Large Language Model qualitative reasoning to deliver personalized, explainable dining recommendations.

---

## 🌟 Key Architecture & Features
- **Frontend Architecture:** Luminous light theme with frosted glassmorphism, dynamic ambient gradient glows, interactive experience presets, custom sliders, and glass cards.
- **Backend Architecture:** High-performance **FastAPI + Uvicorn** asynchronous REST API serving both data endpoints and modern frontend assets.
- **Deployment Ready:** Built for seamless 1-click deployment to **Render.com** via [`render.yaml`](file:///c:/Users/Anumodh/.gemini/antigravity-ide/scratch/Zomato1/render.yaml) or [`Dockerfile`](file:///c:/Users/Anumodh/.gemini/antigravity-ide/scratch/Zomato1/Dockerfile).
- **Data Ingestion Pipeline:** Auto-ingests and normalizes the Hugging Face Zomato dataset (`ManikaSaini/zomato-restaurant-recommendation`) with local sub-second Parquet caching.
- **Deterministic Filtering Engine:** Multi-constraint candidate pruner with 3-stage automated progressive relaxation hierarchy for 0-match resilience.
- **LLM Reasoning & Explainability:** Leverages Google Gemini (`gemini-2.5-flash`) for nuanced trade-off analysis and structured dining verdicts.
- **Zero-Failure Heuristic Fallback:** Embedded rule recommender ensures complete functionality even when offline or without API keys.

---

## 📁 Repository Structure

```
Zomato1/
├── static/                   # High-Performance Frontend Assets
│   ├── css/
│   │   └── style.css         # Luminous light glassmorphic design system
│   ├── js/
│   │   └── app.js            # Async data loading, presets, and AI card renderer
│   └── index.html            # Main Dining Concierge HTML5 interface
├── src/
│   ├── api.py                # FastAPI REST endpoints & static file router
│   ├── config.py             # Global constants, budget thresholds, and paths
│   ├── data/
│   │   ├── cleaner.py        # Data sanitization, ratings/cost parsing
│   │   └── loader.py         # Hugging Face ingestion and Parquet persistence
│   └── engine/
│       ├── filter.py         # Deterministic candidate filtering & progressive relaxation
│       ├── prompt.py         # Prompt engineering & anti-injection sandboxing
│       ├── schemas.py        # Pydantic schemas for request and response validation
│       └── llm_client.py     # Gemini API client & heuristic fallback recommender
├── tests/
│   ├── test_api.py           # FastAPI integration tests
│   ├── test_cleaner.py       # Data cleaner unit tests
│   ├── test_filter.py        # Filtering and relaxation tests
│   └── test_schemas.py       # Schema validation and JSON parser tests
├── main.py                   # Uvicorn entrypoint for local execution & Render.com
├── render.yaml               # Render.com Infrastructure-as-Code blueprint
├── Dockerfile                # Multi-stage production container definition
├── requirements.txt          # Python dependencies
├── .env.example              # Environment configuration template
└── README.md
```

---

## 🚀 Quick Start (Local Execution)

### 1. Set Up Python Environment
```bash
# Using uv (recommended)
uv venv --python 3.11
uv pip install -r requirements.txt

# Or standard pip
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env` and configure your Google Gemini API key:
```bash
cp .env.example .env
```
In `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 3. Launch the Web Application
```bash
.\.venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --reload
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## ☁️ Deploying to Render.com

### Method 1: Render Blueprint (Recommended)
1. Push this repository to GitHub or GitLab.
2. In the [Render Dashboard](https://dashboard.render.com/), click **New +** $\rightarrow$ **Blueprint**.
3. Connect your repository. Render will automatically detect [`render.yaml`](file:///c:/Users/Anumodh/.gemini/antigravity-ide/scratch/Zomato1/render.yaml) and deploy the Web Service.
4. Add your `GEMINI_API_KEY` in the Render Environment Variables tab.

### Method 2: Render Web Service (Manual)
- **Environment:** `Python`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 🧪 Automated Testing

Run the test suite:
```bash
.\.venv\Scripts\pytest.exe tests/ -v
```

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the light glassmorphic frontend UI |
| `GET` | `/health` | Health check endpoint for Render.com |
| `GET` | `/api/metadata` | Returns dataset counts, localities, and cuisines |
| `GET` | `/api/benchmark` | Returns top featured dining spots |
| `POST` | `/api/recommend` | Evaluates candidates and returns AI reasoning predictions |


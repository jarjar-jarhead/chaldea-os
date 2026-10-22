# Chaldea OS // FGO Tactical Command Dashboard

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Google GenAI](https://img.shields.io/badge/Google_GenAI-SDK-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/)
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-Automated_Sync-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)

Chaldea OS is a production-grade tactical dashboard and telemetry comparison suite engineered for Fate/Grand Order (FGO). It provides real-time frontline NP battery calculations, multiplicative damage scaling, dual Saint Graph comparison web charts, and asynchronous AI tactical briefings powered by the Google GenAI SDK.

---

## Key Architectural Features

* **Asynchronous Combat Matrix Solver:** A 3-slot frontline team engine that calculates Turn-1 NP gauge readiness, CE starting charge, Append 2 (Mana Loading), and targetable battery distribution using asynchronous DOM updates (`fetch()` + `history.replaceState()`) with zero full-page reloads.
* **Card-Type Affinity Gating:** Real-time damage multiplier calculation $(1 + \text{ATK}) \times (1 + \text{Card}) \times (1 + \text{NP Dmg})$ that filters card-performance steroids (`Buster`, `Arts`, `Quick`) against the designated Primary DPS Carry's Noble Phantasm card type.
* **Synapse Tactical AI:** Integrates Google's `google-genai` SDK with resilient multi-tier fallback routing (`gemini-1.5-flash` → `gemini-1.5-pro`) and a custom client-side, tag-safe typewriter runner for live debrief streaming.
* **Dual Radar Telemetry:** Interactive Chart.js radar web overlay for side-by-side Servant stat comparison and differential telemetry delta metrics ($\Delta\text{ATK}$, $\Delta\text{HP}$, $\Delta\text{Cost}$).
* **Deterministic Ingestion Pipeline:** Syncs game data directly from Atlas Academy's public exports via custom Django management commands, automatically extracting level-10 skill functions, historical rank-up trees, and targeting enums (`self`, `ptAll`, `ptOne`).
* **Automated Ops & Deployment:** Weekly scheduled GitHub Actions workflow for database synchronization, packaged in a platform-agnostic multi-stage Docker container deployed on Render.

---

## Tech Stack

* **Backend Framework:** Django 5.x (Python 3.11)
* **Database Layer:** SQLite (`db.sqlite3`) with pre-indexed Level-10 skill functions
* **Frontend Design:** Tailwind CSS, Custom Combobox Search Overlays, Chart.js
* **AI Orchestration:** `google-genai` SDK with JSON buffering and HTML streaming
* **Data Provider:** Atlas Academy API Export (`nice_servant.json`)
* **Containerization & CI/CD:** Docker, GitHub Actions, Render

---

## Repository Architecture

```text
chaldea_os/
├── .github/workflows/
│   └── atlas_sync.yml        # Weekly automated DB sync & auto-commit pipeline
├── servants/
│   ├── management/commands/
│   │   └── sync_servants.py  # Atlas Academy API ingestion engine
│   ├── templates/servants/
│   │   ├── compare.html      # Radar web & AI debrief terminal
│   │   ├── team_builder.html # 3-slot battery solver & live comboboxes
│   │   └── servant_detail.html
│   ├── models.py             # Pre-indexed Servant & Battery schema
│   ├── team_engine.py        # Deterministic NP & steroid calculation math
│   └── views.py              # AJAX-backed REST controllers & GenAI wrapper
├── Dockerfile                # Multi-stage production container setup
├── manage.py
└── requirements.txt
```

Quickstart & Local Setup
Prerequisites
Python 3.11+

Git

Google Gemini API Key

1. Clone & Setup Virtual Environment

git clone [https://github.com/your-username/chaldea-os.git](https://github.com/your-username/chaldea-os.git)
cd chaldea-os

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


2. Configure Environment Variables
Create a .env file in the project root:

DEBUG=True
SECRET_KEY=your-django-secret-key
GEMINI_API_KEY=your-google-gemini-api-key
3. Initialize Database & Sync Servant Roster
Run migrations to build the SQLite schema, then ingest game data from Atlas Academy:


python manage.py makemigrations
python manage.py migrate
python manage.py sync_servants

4. Launch Development Server

python manage.py runserver
Navigate to http://127.0.0.1:8000/team/ to access the Frontline Battery Solver.


Docker Deployment
To build and run Chaldea OS inside a standardized container:


# Build Docker image
docker build -t chaldea-os .

# Run container locally
docker run -d -p 8000:8000 --env-file .env chaldea-os

License
Distributed under the MIT License. Data assets sourced via Atlas Academy API. All Fate/Grand Order rights belong to TYPE-MOON, Lasengle, and Aniplex.

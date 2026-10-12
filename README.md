# Nutrix AI – Next-Gen Nutritional Assistant & Health Platform

<div align="center">

![Nutrix AI Banner](https://img.shields.io/badge/Nutrix_AI-Personalized_Health_%26_Nutrition-22c55e?style=for-the-badge&logo=leaf&logoColor=white)

[![Author](https://img.shields.io/badge/Author-Adriyo_Gayen-blue.svg?style=flat-square)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![AI-Engine](https://img.shields.io/badge/LLM-Ollama_%7C_Qwen_3.5_%7C_GLM--OCR-black?style=flat-square&logo=ollama&logoColor=white)](https://ollama.ai/)
[![Database](https://img.shields.io/badge/Storage-MongoDB_%7C_ChromaDB_%7C_SQLite-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Three.js_%7C_GSAP_%7C_Vanilla_JS-FF5722?style=flat-square&logo=javascript&logoColor=white)](https://threejs.org/)

**Author:** **Adriyo Gayen**

*An end-to-end intelligent nutrition ecosystem combining Vision OCR, Regulatory Safety Databases (FSSAI/EU), Hybrid RAG, Personalized Diet Planning, and 3D Interactive Web Experiences.*

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Directory Structure](#-directory-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Quickstart](#-installation--quickstart)
- [Environment Configuration](#-environment-configuration)
- [API Reference](#-api-reference)
- [Running the Pipelines](#-running-the-pipelines)
- [Author & Acknowledgments](#-author--acknowledgments)
- [License](#-license)

---

## 🌿 Overview

**Nutrix AI** (also known as *Healthy Food AI*) is a full-stack, AI-powered health and nutritional intelligence platform. Built with privacy and local execution at its core, Nutrix AI empowers users to take control of their nutritional health by:

1. **Analyzing Food Ingredients via Computer Vision & OCR**: Scan physical food packaging labels to detect hidden additives, allergens, and harmful chemicals, benchmarked against official **FSSAI** and **EU** food safety standards.
2. **Consulting a Context-Aware Nutritional AI**: Chat in real-time with an intelligent assistant backed by **Hybrid RAG** (Retrieval-Augmented Generation), verified medical/nutritional domains, and Open Food Facts data.
3. **Generating Tailored Diet & Macro Plans**: Receive structured, scientifically calibrated daily meal plans tailored to age, BMR, TDEE, weight goals, and dietary restrictions.
4. **Tracking Health & Fitness Goals**: Maintain continuous progress monitoring with simulated wearable pairing and interactive health metric dashboards.
5. **Delivering Cinematic Aesthetics**: Experience a modern, glassmorphic UI featuring a 3D interactive room with a pull-chain lamp powered by **Three.js** and fluid **GSAP** animations.

---

## 🚀 Key Features

### 🤖 1. Streaming Nutritional AI Assistant
- **Hybrid RAG Pipeline**: Combines keyword search (BM25/FTS) and vector similarity search across pre-indexed nutrition databases (`nutrix_rag.db`, `nutrix_web.db`).
- **Real-Time Streaming**: Delivers instant NDJSON token streaming with interactive status indicators (e.g. `[UI: Searching trusted sources...]`).
- **Verified Sources & Open Food Facts**: Pulls live product metadata and cross-references assertions against whitelisted health authorities.
- **Session-Based Chat Persistence**: Conversations are saved to **MongoDB** with multi-session isolation and history retrieval.

### 🔍 2. Smart Ingredient Scanner & Label OCR
- **Multimodal Vision OCR**: Processes packaging images using local vision models (`glm-ocr`) and Tesseract fallback.
- **Regulatory Safety Rule Matching**: Automatic cross-referencing against FSSAI and European Union safety statuses for food additives, preservatives, and emulsifiers.
- **Deep Health Risk Assessment**: Highlights clean ingredients, flags high-risk chemicals, and provides human-readable explanations of potential side effects.
- **Scan History Ledger**: Retains scanned items and AI verdicts securely in MongoDB.

### 🥗 3. Intelligent Diet & Macro Planner
- **Biometric Calculations**: Computes Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE).
- **Customized Meal Schedules**: Generates breakfast, lunch, snack, and dinner breakdowns with exact macronutrient (protein, carbs, fat) and micronutrient balances.
- **ChromaDB Vector Storage**: Embeds and indexes generated plans for fast contextual retrieval and comparative analysis.

### 🎯 4. Fitness & Goal Tracker
- **Progress Visualizations**: Interactive progress rings, calorie burn trackers, and macronutrient targets.
- **Device Pairing Simulation**: Simulated synchronization with smartwatches/wearables (Apple Health, Garmin, Fitbit).

### 🎨 5. Immersive 3D & Micro-Animated UI
- **Interactive 3D Room**: A custom **Three.js** WebGL scene featuring a realistic vintage lamp with dynamic lighting and interactive mouse/touch chain pulling.
- **Smooth GSAP Motion**: Polished page reveals, ambient glowing cursor followers, and dynamic glassmorphism panels.
- **Zero Heavy Framework Bloat**: Lightning-fast vanilla HTML5, CSS3, and modern JavaScript without heavy frontend framework overhead.

---

## 🏗️ System Architecture

```text
               +--------------------------------------------------+
               |              Nutrix AI Web Client                |
               |   Vanilla JS • Three.js (3D Lamp) • GSAP • CSS3  |
               +------------------------+-------------------------+
                                        | HTTP / Streaming NDJSON
                                        v
               +--------------------------------------------------+
               |              FastAPI Gateway (Port 8000)         |
               |  Supabase JWT / OAuth • Rate Limiting • CORS     |
               +------------------------+-------------------------+
                                        |
      +---------------------------------+---------------------------------+
      |                                 |                                 |
      v                                 v                                 v
+------------------+         +--------------------+            +-------------------+
|  Chat & RAG Core |         | Vision & OCR Core  |            | Diet Planner Core |
| NutrixIntelligence|        |   glm-ocr / Vision |            |   BMR/TDEE Engine |
|  Hybrid Retrieval|         | SQLite Rule Engine |            |   LLM Formulation |
+--------+---------+         +---------+----------+            +---------+---------+
         |                             |                                 |
         +-----------------------------+---------------------------------+
                                        |
                                        v
+----------------------------------------------------------------------------------+
|                              AI & Persistence Layer                              |
|                                                                                  |
|  • Ollama Local LLMs:  qwen3.5:9b (Reasoning) & glm-ocr (Vision Extraction)      |
|  • MongoDB Atlas:      Chat sessions, scan logs, user input telemetry            |
|  • ChromaDB:           Vector embeddings for personalized diet plans             |
|  • SQLite Databases:   nutrix_rag.db (FSSAI/EU Rules, Cifocoss food statistics)  |
|  • Supabase:           User identity, authentication tokens, and profile sync   |
+----------------------------------------------------------------------------------+
```

---

## 🛠️ Technology Stack

| Layer | Technologies & Tools |
| :--- | :--- |
| **Author** | **Adriyo Gayen** |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), Python 3.10+ |
| **Local AI & LLMs** | [Ollama](https://ollama.ai/) (`qwen3.5:9b`, `glm-ocr`), Mistral AI API fallback |
| **Vision & OCR** | GLM-OCR, [PyTesseract](https://pypi.org/project/pytesseract/), OpenCV, Pillow, Docling |
| **Databases & Vector Stores**| [MongoDB](https://www.mongodb.com/) (Motor async), [ChromaDB](https://www.trychroma.com/), SQLite3, SQLAlchemy |
| **Authentication** | [Supabase Auth](https://supabase.com/) (JWT), Google OAuth 2.0, Passlib (Bcrypt) |
| **Frontend & UI** | Vanilla HTML5/CSS3, [Three.js](https://threejs.org/) (WebGL 3D), [GSAP 3](https://greensock.com/gsap/) |
| **Data Science & RAG** | Pandas, NumPy, Scikit-learn, BeautifulSoup4, Open Food Facts API |

---

## 📁 Directory Structure

```text
project/
├── .env.example                     # Sample environment variable template
├── .gitignore                       # Git exclusion rules (OS, caches, logs, DBs)
├── README.md                        # Project documentation (Author: Adriyo Gayen)
├── pyproject.toml                   # Project configuration and metadata
├── requirement.txt                  # Python dependencies
├── start_pipeline.sh                # Automation script to start backend & frontend
├── stop_pipeline.sh                 # Pipeline termination script
├── embed_csv.py                     # Script to seed RAG food consumption stats
│
├── frontend/                        # Client-side presentation tier
│   ├── index.html                   # Cinematic 3D interactive login portal
│   ├── login.css / login.js         # Three.js 3D lamp mechanics & auth logic
│   ├── dashboard.html               # Main user hub & feature navigation
│   ├── dashboard_new.css / .js      # Dashboard styling and GSAP animations
│   ├── chat.html / chat.js          # Streaming nutritional AI chat interface
│   ├── scanner.html / scanner.js    # Label upload & ingredient breakdown UI
│   ├── planner.html / planner.js    # Personalized diet generation portal
│   ├── goal_tracker.html            # Daily nutrition & fitness tracker
│   ├── profile.html / profile.js    # User settings and dietary preferences
│   ├── server_no_cache.py           # Local development HTTP server (Port 3000)
│   └── images/                      # Media assets & background videos
│
└── Scource code/                    # Core backend and AI pipelines
    └── nutrix_ai/
        ├── api.py                   # Main FastAPI application & route endpoints
        ├── auth.py                  # Token encoding, hashing, and credentials
        ├── security.py              # Supabase JWT token verification
        ├── database.py              # SQLite models & database session bindings
        ├── mongodb.py               # Async MongoDB interface (chats, scans)
        ├── chroma_diet_store.py     # ChromaDB vector store for diet plans
        ├── unified_analyzer.py      # Vision OCR + FSSAI/EU rule analyzer
        ├── diet_planner.py          # BMR/TDEE calculation and prompt orchestration
        ├── config/                  # Configuration mappings (e.g. trusted domains)
        ├── core/
        │   └── nutrix_intelligence.py # Master RAG orchestrator & fallback loop
        ├── indexing/                # Dual indexers (BM25 keyword + vector DB)
        ├── retrieval/               # RAG retrievers & OpenFoodFacts connector
        ├── routing/                 # Semantic query router and intent classifier
        └── user/                    # User health profile & dietary context
```

---

## ⚙️ Prerequisites

Before launching Nutrix AI, ensure the following prerequisites are installed:

1. **Python 3.10 or higher** (Python 3.11 – 3.13 supported).
2. **Ollama**: Installed and running locally on port `11434`.
   ```powershell
   # Pull the required models
   ollama pull qwen3.5:9b
   ollama pull glm-ocr
   ```
3. **MongoDB**: Either a local instance (`mongodb://localhost:27017`) or a free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster.
4. **Tesseract OCR** (Optional fallback): Ensure Tesseract is installed on your system path if testing legacy OCR routes.

---

## 🏃 Installation & Quickstart

### 1. Clone & Setup Workspace

```powershell
# Clone the repository
git clone <repository_url>
cd "project"

# Create and activate Python virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```powershell
pip install -r requirement.txt
```

### 3. Configure Environment Variables

Copy the provided sample `.env.example` file to create your active `.env`:

```powershell
cp .env.example .env
```

Edit `.env` with your preferred settings:
```ini
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1/chat/completions
OLLAMA_MODEL=qwen3.5:9b
MONGODB_URI=mongodb://localhost:27017/nutrix_db
JWT_SECRET_KEY=generate_a_secure_random_hex_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_publishable_key
```

---

## 🚦 Running the Application

### Option A: Automated Pipeline (Bash / WSL / Git Bash)

```bash
chmod +x start_pipeline.sh stop_pipeline.sh
./start_pipeline.sh
```

To stop all services:
```bash
./stop_pipeline.sh
```

---

### Option B: Manual Execution (Two Terminals)

#### Terminal 1 — Start the FastAPI Backend:
```powershell
# From the project root
python "Scource code/nutrix_ai/api.py"
```
*Backend API service starts at `http://localhost:8000`.*
*Interactive OpenAPI documentation available at `http://localhost:8000/docs`.*

#### Terminal 2 — Start the Frontend Development Server:
```powershell
# From the project root
python "frontend/server_no_cache.py"
```
*Frontend service starts at `http://localhost:3000`.*

---

### 3. Open in Browser

Open your browser and navigate to:
```text
http://localhost:3000
```
- Click **ENTER** on the splash screen.
- Interact with the **3D Lamp** by pulling the lamp chain to turn on the room light and reveal the login credentials panel.
- Log in or register to access the **Dashboard**, **Nutritional AI Chat**, **Ingredient Scanner**, and **Diet Planner**.

---

## 📡 API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/register` | Register a new user profile with initial dietary goals | No |
| `POST` | `/login` | Authenticate using email and password, returns JWT | No |
| `POST` | `/auth/google` | Verify Google OAuth identity token | No |
| `GET` | `/user/profile` | Retrieve the authenticated user's profile | Bearer Token |
| `GET/POST`| `/user/preferences`| Read or update UI preferences (theme, language, state) | Bearer Token |
| `POST` | `/chat` | Standard RAG conversational query (MongoDB recorded) | Bearer Token |
| `POST` | `/chat/stream` | Real-time NDJSON streaming AI response with UI state | Bearer Token |
| `GET` | `/chat/history` | Retrieve user chat transcript history | Bearer Token |
| `DELETE`| `/chat/history` | Delete user chat history or specific session | Bearer Token |
| `POST` | `/analyze-label` | Upload label image: OCR + FSSAI/EU rule check | Bearer Token |
| `GET` | `/scans/history` | Retrieve prior ingredient scans and risk ratings | Bearer Token |
| `DELETE`| `/scans/history` | Clear scanned ingredients ledger | Bearer Token |
| `POST` | `/diet-plan` | Generate personalized meal plan (MongoDB + ChromaDB) | Bearer Token |
| `GET` | `/diet-plans/history`| Retrieve stored diet plans and input parameters | Bearer Token |
| `DELETE`| `/diet-plans/history`| Purge all stored diet plans from MongoDB & ChromaDB | Bearer Token |
| `GET` | `/fitness/status` | Retrieve fitness tracker synchronization status | Bearer Token |
| `POST` | `/fitness/pair` | Pair simulated wearable fitness tracker | Bearer Token |
| `POST` | `/fitness/unpair` | Unpair connected wearable device | Bearer Token |

---

## 🛡️ Food Safety & Regulatory Intelligence

The **Ingredient Scanner** checks extracted compounds against a curated SQLite rule repository containing:
- **FSSAI Status** (Food Safety and Standards Authority of India)
- **EU Approval & Ban Status** (European Food Safety Authority)
- **Primary Health Risks**: Carcinogenicity, endocrine disruption, digestive inflammation, metabolic disruption, and allergen alerts.

---

## 👨‍💻 Author & Acknowledgments

- **Lead Architect & Developer:** **Adriyo Gayen**
- **Special Thanks:**
  - The [Ollama](https://ollama.ai/) team for local LLM inference tooling.
  - The [Three.js](https://threejs.org/) and [GSAP](https://greensock.com/) communities for creative WebGL and motion graphics libraries.
  - [Open Food Facts](https://world.openfoodfacts.org/) for public nutritional and ingredient datasets.

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and distribute for personal, educational, and commercial applications.

# Talent Intelligence Platform 🤖📈

A premium, AI-powered multi-agent recruitment dashboard for parsing resumes, scoring candidates with Gemini LLM, and orchestrating your hiring pipeline.

## 🚀 Features
- **AI-Powered Matching**: Uses Google Gemini to analyze skills, experience, and project depth beyond simple keyword search.
- **Original File Store**: Retains binary originals (PDF/Docx) for direct recruiter download.
- **Multi-Agent Pipeline**: Heuristic extraction with LLM fallback for 100% data reliability.
- **Audit-Ready**: Transparent logs for every AI decision.
- **Bulk Orchestration**: Manage email and interview scheduling directly in one view.

## 🛠️ Local Setup (Docker)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/talent-iq.git
   cd talent-iq
   ```

2. **Configure Environment Variables**:
   Create a `.env` file (copy from `.env.example`):
   ```env
   DATABASE_URL=postgresql+asyncpg://talent:talentpass@db:5432/talentdb
   REDIS_URL=redis://redis:6379/0
   SECRET_KEY=your_random_secret_key
   
   # AI Matching
   ENABLE_GEMINI=True
   GEMINI_API_KEY=your_google_ai_key
   ```

3. **Spin up the stack**:
   ```bash
   docker-compose up --build
   ```

4. **Access the platform**:
   - **Frontend (Streamlit)**: `http://localhost:8501`
   - **Backend API Docs**: `http://localhost:8000/docs`

## ☁️ Deployment Strategy

### 1. Backend (FastAPI + Postgres)
Deploy the API and Database to a platform like **Render**, **Railway**, or **AWS ECS**.
- Ensure the `DATABASE_URL` and `REDIS_URL` point to your production instances.

### 2. Frontend (Streamlit Cloud)
Connect your GitHub repo to Streamlit Cloud.
- **Main path**: `streamlit_app/app.py`
- **Secrets**: Provide `API_BASE_URL` pointing to your hosted FastAPI backend.

## 📄 License
MIT License. Created by Antigravity.

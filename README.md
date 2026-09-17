# AI Recruitment SaaS

A modern recruitment platform built with FastAPI backend and React frontend. This is a monorepo containing both the backend API and frontend application.

## 📁 Project Structure

```
AI-Recruitment-SaaS/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Request/response schemas
│   │   ├── services/ # Business logic
│   │   ├── core/     # Configuration & security
│   │   └── dependencies/ # Dependency injection
│   ├── requirements.txt
│   └── .env          # Backend environment variables
│
├── frontend/         # React frontend
│   ├── public/        # Static files
│   ├── src/           # Pages, components, context, and API client
│   ├── package.json
│   └── .env           # Frontend environment variables
│
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## 🚀 Getting Started

### Backend Setup

1. Navigate to backend folder:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp ../.env.example .env  # Then copy the backend section into backend/.env
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

### Frontend Setup

1. Navigate to frontend folder:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env  # Or update the existing .env file
```

4. Run development server:
```bash
npm run dev
```

The React app runs at `http://localhost:3000`.

## 🔧 Environment Variables

Each folder has its own `.env` file:
- `backend/.env` - Backend API configuration
- `frontend/.env` - Frontend API configuration

Use the root `.env.example` for backend variables and `frontend/.env.example` for frontend variables. Keep real `.env` files uncommitted.

For local development, `frontend/.env` should contain:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

## 📚 Key Features

- **User Authentication** - JWT-based authentication
- **Company Management** - Multi-tenant support with role-based access and company CRUD
- **Job Postings** - Select a company, create jobs, and view jobs for the selected company
- **Candidate Profiles** - Candidates can manage their profiles and resumes
- **Resume Upload** - PDF resume storage with Supabase
- **Permissions System** - Role-based access control (OWNER, HR, RECRUITER, COMPANY_ADMIN, CANDIDATE)
- **Responsive UI** - Shared styling, responsive layouts, active navigation, and page back navigation

## Frontend Workflow

1. Register a user and log in.
2. Open **Companies** and create or select a company.
3. Open **Jobs**, select a company, and click **Post a New Job**.
4. Complete the job form and submit it. Jobs are created through `POST /companies/{company_id}/jobs`.

The back button is available on child pages and is intentionally hidden on the dashboard because the dashboard is the main page.

For the complete backend endpoint mapping, see [API_ENDPOINT_REPORT.md](API_ENDPOINT_REPORT.md).

## 🏗️ Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Supabase (File storage)
- JWT (Authentication)

**Frontend:**
- React 18
- React Router
- Axios
- CSS design system with responsive styles

## 📝 License

This project is proprietary.
# AI-Recruitment-SaaS

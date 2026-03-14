# SafeDroid – App Risk Analyzer

<<<<<<< HEAD
BACKEND
cd backend
python -m venv venv
venv\Scripts\activate  
pip install fastapi uvicorn sqlalchemy google-play-scraper
pip freeze > requirements.txt

python seed_db.py # Set up the database (run this ONCE only)
# You should see: ✅ Database seeded successfully → safedroid.db
python uvicorn main:app --reload

FRONTEND
cd frontend
npm install
mpn run dev


⚠️ If you see a nested frontend/frontend folder 
run: rm -rf frontend/frontend
Then proceed with npm install normally.


NECESSARY GIT COMMANDS

To pull : 
git pull origin master

To commit :
git add .
git commit -m "describe what they changed"

To push :
git push origin master

=======

A web application that analyzes the security risk of mobile apps based on their requested permissions.
>>>>>>> 980cc9d43c7b757a060089373c64d8590671ce63

---

## Prerequisites

- Python 3.8+ with `venv` module
- Node.js 16+ with npm
- SQLite (included with Python)

---

## Setup (One-time)

**1. Clone/Download this project and navigate to it:**

```bash
cd path/to/SafeDroid
```

**2. Create Python virtual environment:**

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install Python dependencies:**

```bash
pip install -r backend/requirements.txt
```

**4. Install Node dependencies:**

```bash
cd frontend
npm install
cd ..
```

---

## How to Run

**Open 2 terminals in your SafeDroid project directory:**

### Terminal 1 - Backend

**Windows:**
```powershell
.venv\Scripts\Activate.ps1
$env:DATABASE_URL='sqlite:///./safedroid.db'
python -m uvicorn backend.main:app --port 8000
```

**Mac/Linux:**
```bash
source .venv/bin/activate
export DATABASE_URL='sqlite:///./safedroid.db'
python -m uvicorn backend.main:app --port 8000
```

**Stop when you see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Important:** Keep this terminal open. Do NOT close it.

---

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

**Stop when you see:**
```
✔  Local:   http://localhost:5176/
```

---

### Step 3 - Open Your Browser

Go to: **http://localhost:5176/**

You should see the SafeDroid app with a list of apps to analyze!

## Features

- **Scan Apps**: Quickly scan an app to see its risk score and permissions
- **Search**: Find apps by name or Play Store URL
- **Analyze**: Get detailed permission analysis with privacy impact assessment
- **Detect Threats**: Identify suspicious permission patterns and threat indicators
- **Compare**: Compare multiple apps side by side
- **Browse Permissions**: View all permission metadata by category

## Database

- **SQLite (default)**: Uses `safedroid.db` in the project root for local development
- **PostgreSQL**: To use PostgreSQL, ensure the database exists and set `DATABASE_URL` before running the backend

## Project Structure

```
SafeDroid/
├── backend/
│   ├── main.py            # FastAPI application
│   ├── database.py        # SQLAlchemy models and database setup
│   ├── risk_engine.py     # Permission analysis logic
│   ├── app_data.py        # Permission metadata (small dataset)
│   ├── app_data_full.py   # Permission metadata (extended dataset)
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── src/
    │   ├── App.jsx        # Main React component
    │   └── App.css        # Styling
    ├── package.json       # Node dependencies
    └── vite.config.js     # Vite configuration
```

## Troubleshooting

**Backend won't start?**
- Make sure you've activated the virtual environment
- Check that port 8000 is not in use: `netstat -ano | findstr :8000`
- Verify all dependencies are installed: `pip install -r requirements.txt`

**Frontend shows no data?**
- Ensure the backend is running and accessible at http://localhost:8000
- Check your browser console for CORS or network errors
- Try refreshing the page after the backend is running

**Database issues?**
- Delete `safedroid.db` and restart the backend to reinitialize
- For PostgreSQL, ensure the `safedroid` database exists

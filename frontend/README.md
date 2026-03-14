# SafeDroid Frontend

React + Vite frontend for SafeDroid.

## Prerequisites

- Node.js 16+ with npm installed
- Backend running at http://127.0.0.1:8000 (see main README)

## Running the Backend First

From the project root, activate the Python environment and start the backend.

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

You'll see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open.** Then proceed to the frontend in a new terminal.

## Running the Frontend

From the project root, start the frontend:

```bash
cd frontend
npm run dev
```

You should see:
```
✔  Local:   http://localhost:5176/
```

Then open your browser to: **http://localhost:5176/**








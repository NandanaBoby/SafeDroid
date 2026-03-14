# SafeDroid Backend

FastAPI-based backend for the SafeDroid app security risk analyzer.

## Prerequisites

- Python 3.8+ with venv
- Dependencies from `requirements.txt`

## Running the Backend

From the project root:

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

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open while using the app.**

## Database Options

### SQLite (Local Development - Recommended)

Set environment variable:

**Windows:**
```powershell
$env:DATABASE_URL='sqlite:///./safedroid.db'
```

**Mac/Linux:**
```bash
export DATABASE_URL='sqlite:///./safedroid.db'
```

Then run uvicorn as shown above.

### PostgreSQL (Production)

First, create the database:

```sql
CREATE DATABASE safedroid;
```

Then set the environment variable:

**Windows:**
```powershell
$env:DATABASE_URL='postgresql://postgres:password@localhost:5432/safedroid'
```

**Mac/Linux:**
```bash
export DATABASE_URL='postgresql://postgres:password@localhost:5432/safedroid'
```

Then run uvicorn as shown above.

## Project Structure

```
backend/
├── main.py              # FastAPI application and endpoints
├── database.py          # SQLAlchemy models and database setup
├── risk_engine.py       # Permission analysis and risk scoring logic
├── app_data.py          # Permission metadata (basic dataset)
├── app_data_full.py     # Permission metadata (extended dataset with 30+ apps)
├── requirements.txt     # Python dependencies
└── __init__.py          # Package initialization
```

## API Endpoints

### Apps

- **GET** `/apps` - Get list of all available apps
- **GET** `/health` - Health check endpoint

### Analysis

- **POST** `/scan` - Quick risk scan for an app
- **POST** `/search` - Search for an app by name or Play Store URL
- **POST** `/analyze` - Comprehensive app analysis
- **POST** `/detect-threats` - Detect threat indicators and suspicious patterns
- **POST** `/bulk-analyze` - Analyze multiple apps
- **POST** `/compare` - Compare multiple apps side by side

### Permissions

- **GET** `/permissions` - Get permission metadata (with optional category filtering)
- **GET** `/permission-categories` - Get all permission categories
- **POST** `/analyze-permissions` - Analyze a custom list of permissions

## Database

The application uses SQLAlchemy ORM with support for both SQLite and PostgreSQL.

### Models

- **App**: Core app data with permissions and risk scores
- **RiskProfile**: Detailed risk assessment for each app
- **PermissionJustification**: Explanations for permission requests

### Seeding

The database is automatically seeded on startup with 31 apps from `APP_PERMISSION_DATA` defined in the data modules. Apps are only seeded once; subsequent runs skip the seeding if data already exists.

## Permission Metadata

Permission data is organized into two modules:

- **app_data.py**: Contains core permissions and a basic app dataset
- **app_data_full.py**: Extended dataset with additional apps and metadata

The system automatically tries to import from `app_data_full` first, with fallback to `app_data` for compatibility.

## Risk Scoring

The risk engine analyzes apps using:

1. **Severity Scores**: Each permission is rated 0-10 based on privacy/security impact
2. **Correlation Analysis**: Detects suspicious permission combinations
3. **Threat Detection**: Identifies malware patterns (e.g., device admin + SMS)
4. **Privacy Impact**: Categorizes data access by sensitivity
5. **Risk Levels**: Maps scores to levels (LOW, MEDIUM, HIGH, CRITICAL)

## Troubleshooting

**Port already in use?**
```powershell
netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force
```

**Database locked (SQLite)?**
- Close all Python processes and restart the server

**Import errors?**
- Ensure the virtual environment is activated
- Run `pip install -r requirements.txt` again

**CORS issues?**
- CORS is enabled for all origins by default (see `main.py`)
- Adjust `allow_origins` if needed for security

## Development

The server runs in reload mode with `--reload`, so changes to code are automatically reflected (requires restart of the process).

For production, remove the `--reload` flag and consider using Gunicorn with multiple workers:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from urllib.parse import urlparse, parse_qs
from sqlalchemy.orm import Session

# use package-qualified imports so the module can be executed
# from outside the directory (e.g. uvicorn backend.main:app)
# import the analyzer; try a relative import first (package mode),
# otherwise fall back to bare module import when running directly
# within the backend folder.
try:
    from .risk_engine import calculate_risk, analyze_app, PermissionAnalyzer
except ImportError:  # module not recognized as package
    from risk_engine import calculate_risk, analyze_app, PermissionAnalyzer

# Import from app_data_full first (has more apps), fallback to app_data
# also expose APP_PERMISSION_DATA in case any future endpoints or utilities
# need direct access to the raw dataset.
# imports of data modules should also be package-qualified when
# running from the project root.  fall back to the smaller dataset if
# the full one is not available.
# data imports: we use the same try/except pattern so the code is
# importable both when running as a module (backend.main) and when
# invoked directly from the backend directory.
try:
    from .app_data_full import (
        PERMISSION_METADATA,
        PERMISSION_CATEGORIES,
        PACKAGE_NAME_MAP,
        APP_PERMISSION_DATA,
    )
except ImportError:  # not a package context or full file not available
    try:
        from .app_data import (
            PERMISSION_METADATA,
            PERMISSION_CATEGORIES,
            PACKAGE_NAME_MAP,
            APP_PERMISSION_DATA,
        )
    except ImportError:
        # fallback when run inside backend without package context
        from app_data_full import (
            PERMISSION_METADATA,
            PERMISSION_CATEGORIES,
            PACKAGE_NAME_MAP,
            APP_PERMISSION_DATA,
        )
        # if that fails it'll raise and surface the real issue

# database module may be loaded as part of package or directly
try:
    from .database import App, init_db, seed_database, get_db
except ImportError:
    from database import App, init_db, seed_database, get_db

app = FastAPI(title="SafeDroid – App Risk Analyzer", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend - comment out for development if frontend is run separately
try:
    app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="frontend")
except RuntimeError:
    print("Frontend directory not found - API-only mode")


# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database and seed data on startup"""
    try:
        init_db()
        print("Database tables created successfully!")
        seed_database()
        print("Database initialization complete!")
    except Exception as e:
        print(f"Database initialization warning: {e}")


# Pydantic models

class AppScanRequest(BaseModel):
    app_name: str = Field(..., description="Name of the app to scan")


class PermissionListRequest(BaseModel):
    permissions: List[str] = Field(..., description="List of permission names to analyze")


class BulkScanRequest(BaseModel):
    app_names: List[str] = Field(..., description="List of app names to scan")


class SearchRequest(BaseModel):
    query: str = Field(..., description="App name or Play Store URL to search")


# Database helper functions

def get_app_from_db(db: Session, app_name: str) -> Optional[App]:
    """Get app from PostgreSQL database"""
    return db.query(App).filter(App.name.ilike(app_name)).first()


def get_all_apps_from_db(db: Session) -> List[App]:
    """Get all apps from PostgreSQL database"""
    return db.query(App).order_by(App.name).all()


# Helpers

def resolve_query_to_app_name(query: str, db: Session = None) -> Optional[str]:
    """Resolves a raw search query (app name OR Play Store URL) to a known app name"""
    query = query.strip()
    lower_query = query.lower()

    # First try database if available
    if db:
        app = get_app_from_db(db, lower_query)
        if app:
            return app.name

    # Direct case-insensitive match against PACKAGE_NAME_MAP
    for key in PACKAGE_NAME_MAP:
        if key.lower() == lower_query:
            return PACKAGE_NAME_MAP[key]

    # Try to parse as a URL and extract package name
    package_id = None
    try:
        parsed = urlparse(query)
        if parsed.scheme in ("http", "https"):
            params = parse_qs(parsed.query)
            if "id" in params:
                package_id = params["id"][0].lower()
    except Exception:
        pass

    if package_id:
        if package_id in PACKAGE_NAME_MAP:
            return PACKAGE_NAME_MAP[package_id]
        for keyword, app_name in PACKAGE_NAME_MAP.items():
            if keyword in package_id or package_id in keyword:
                return app_name

    # Substring keyword match on raw query
    for keyword, app_name in PACKAGE_NAME_MAP.items():
        if keyword in lower_query or lower_query in keyword:
            return app_name

    # Try database for partial match
    if db:
        apps = get_all_apps_from_db(db)
        for app in apps:
            if lower_query in app.name.lower():
                return app.name

    return None


# Endpoints

@app.post("/search")
def search_app(data: SearchRequest, db: Session = Depends(get_db)):
    """Search for an app by name or Play Store URL"""
    resolved = resolve_query_to_app_name(data.query, db)

    if not resolved:
        raise HTTPException(status_code=404, detail=f"Could not find a matching app for: '{data.query}'")

    app = get_app_from_db(db, resolved)
    if app:
        score, level, explanations = calculate_risk(app.permissions or [])
        return {
            "app_name": app.name,
            "resolved_from": data.query,
            "extracted_permissions": app.permissions or [],
            "risk_score": app.risk_score or score,
            "risk_level": app.risk_level or level,
            "explanations": explanations,
            "version": app.version,
            "package_name": app.package_name
        }

    raise HTTPException(status_code=404, detail=f"Could not find a matching app for: '{data.query}'")


@app.post("/scan")
def scan_app(data: AppScanRequest, db: Session = Depends(get_db)):
    """Basic app risk scanning"""
    app_name = data.app_name

    app = get_app_from_db(db, app_name)
    if app:
        score, level, explanations = calculate_risk(app.permissions or [])
        return {
            "app_name": app.name,
            "extracted_permissions": app.permissions or [],
            "risk_score": app.risk_score or score,
            "risk_level": app.risk_level or level,
            "explanations": explanations
        }

    raise HTTPException(status_code=404, detail="App not found in database")


@app.post("/analyze")
def analyze_app_comprehensive(data: AppScanRequest, db: Session = Depends(get_db)):
    """Comprehensive app analysis with detailed permission breakdown"""
    app_name = data.app_name

    app = get_app_from_db(db, app_name)
    if app:
        result = analyze_app(app.name)
        if "error" not in result:
            result["from_database"] = True
            result["version"] = app.version
            result["package_name"] = app.package_name
            return result

    result = analyze_app(app_name)
    if "error" in result:
        raise HTTPException(status_code=404, detail="App not found in database")

    result["from_database"] = False
    return result


@app.post("/analyze-permissions")
def analyze_permissions(data: PermissionListRequest):
    """Analyze a custom list of permissions for risk assessment"""
    analyzer = PermissionAnalyzer()

    invalid_perms = [p for p in data.permissions if p not in PERMISSION_METADATA]
    if invalid_perms:
        return {
            "warning": f"Unknown permissions: {invalid_perms}",
            "valid_permissions": [p for p in data.permissions if p in PERMISSION_METADATA]
        }

    severity_analysis = analyzer.calculate_severity_score(data.permissions)
    correlation_analysis = analyzer.detect_permission_correlations(data.permissions)
    privacy_analysis = analyzer.analyze_privacy_impact(data.permissions)
    categorized = analyzer.categorize_permissions(data.permissions)

    total_score = severity_analysis["total_score"]
    risk_level = analyzer.calculate_risk_level(total_score)

    return {
        "permissions_count": len(data.permissions),
        "risk_score": total_score,
        "risk_level": risk_level,
        "severity_analysis": severity_analysis,
        "correlation_analysis": correlation_analysis,
        "privacy_analysis": privacy_analysis,
        "categorized_permissions": categorized
    }


@app.post("/detect-threats")
def detect_threats(data: AppScanRequest, db: Session = Depends(get_db)):
    """Detect specific threat indicators and suspicious patterns in an app"""
    app_name = data.app_name

    app = get_app_from_db(db, app_name)
    if app:
        analyzer = PermissionAnalyzer()
        threat_indicators = analyzer.detect_threat_indicators(app.name)
        permissions = app.permissions or []
        correlations = analyzer.detect_permission_correlations(permissions)

        return {
            "app_name": app.name,
            "threat_indicators": threat_indicators,
            "suspicious_patterns": correlations["suspicious_patterns"],
            "pattern_risk_level": correlations["pattern_risk_level"],
            "permissions": permissions,
            "risk_score": app.risk_score,
            "risk_level": app.risk_level
        }

    analyzer = PermissionAnalyzer()
    threat_indicators = analyzer.detect_threat_indicators(app_name)
    correlations = analyzer.detect_permission_correlations([])

    return {
        "app_name": app_name,
        "threat_indicators": threat_indicators,
        "suspicious_patterns": correlations["suspicious_patterns"],
        "pattern_risk_level": correlations["pattern_risk_level"]
    }


@app.post("/bulk-analyze")
def bulk_analyze(data: BulkScanRequest, db: Session = Depends(get_db)):
    """Analyze multiple apps and return comparative risk summary"""
    results = []

    for app_name in data.app_names:
        app = get_app_from_db(db, app_name)
        if app:
            result = analyze_app(app.name)
            if "error" not in result:
                result["risk_score"] = app.risk_score
                result["risk_level"] = app.risk_level
                results.append(result)

    if not results:
        raise HTTPException(status_code=404, detail="No valid apps found")

    risk_levels = [r["risk_level"] for r in results]
    avg_score = sum(r["risk_score"] for r in results) / len(results)

    return {
        "total_apps_analyzed": len(results),
        "average_risk_score": round(avg_score, 2),
        "risk_level_distribution": {
            "CRITICAL": risk_levels.count("CRITICAL"),
            "HIGH": risk_levels.count("HIGH"),
            "MEDIUM": risk_levels.count("MEDIUM"),
            "LOW": risk_levels.count("LOW")
        },
        "apps": results
    }


@app.get("/permissions")
def get_permissions(category: Optional[str] = None):
    """Get permission metadata with optional category filtering"""
    if category:
        if category not in PERMISSION_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        filtered_perms = {p: meta for p, meta in PERMISSION_METADATA.items() if meta.get("category") == category}
        return {"category": category, "permissions": filtered_perms}
    return PERMISSION_METADATA


@app.get("/permission-categories")
def get_permission_categories():
    """Get all permission categories and their descriptions"""
    return PERMISSION_CATEGORIES


@app.get("/apps")
def get_available_apps(db: Session = Depends(get_db)):
    """Get list of all available apps in the database"""
    apps = get_all_apps_from_db(db)
    
    if apps:
        return [{
            "name": app.name,
            "version": app.version,
            "risk_level": app.risk_level,
            "permissions_count": len(app.permissions) if app.permissions else 0,
            "risk_score": app.risk_score
        } for app in apps]
    
    return []


@app.post("/compare")
def compare_apps(data: BulkScanRequest, db: Session = Depends(get_db)):
    """Compare multiple apps and provide detailed comparison"""
    if len(data.app_names) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 apps to compare")

    analyzer = PermissionAnalyzer()
    apps_data = []

    for app_name in data.app_names:
        app = get_app_from_db(db, app_name)
        if app:
            permissions = app.permissions or []
            severity = analyzer.calculate_severity_score(permissions)
            apps_data.append({
                "app_name": app.name,
                "risk_score": app.risk_score or severity["total_score"],
                "permission_count": len(permissions),
                "dangerous_count": severity["critical_count"] + severity["dangerous_count"],
                "critical_permissions": severity["severity_breakdown"]["critical"],
                "risk_level": app.risk_level
            })

    if not apps_data:
        raise HTTPException(status_code=404, detail="No valid apps found")

    return {
        "comparison": apps_data,
        "highest_risk": max(apps_data, key=lambda x: x["risk_score"])["app_name"],
        "lowest_risk": min(apps_data, key=lambda x: x["risk_score"])["app_name"]
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    apps_count = db.query(App).count() if db else 0
    return {
        "status": "healthy",
        "version": "2.0.0",
        "apps_in_database": apps_count,
        "permissions_tracked": len(PERMISSION_METADATA),
        "database": "postgresql"
    }

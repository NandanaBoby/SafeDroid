from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from urllib.parse import urlparse, parse_qs

from risk_engine import calculate_risk, analyze_app, PermissionAnalyzer
from app_data import APP_PERMISSION_DATA, PERMISSION_METADATA, PERMISSION_CATEGORIES, PACKAGE_NAME_MAP

app = FastAPI(title="SafeDroid – App Risk Analyzer", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="frontend")


# ── Pydantic models ────────────────────────────────────────────────────────────

class AppScanRequest(BaseModel):
    app_name: str = Field(..., description="Name of the app to scan")


class PermissionListRequest(BaseModel):
    permissions: List[str] = Field(..., description="List of permission names to analyze")


class BulkScanRequest(BaseModel):
    app_names: List[str] = Field(..., description="List of app names to scan")


class SearchRequest(BaseModel):
    query: str = Field(..., description="App name or Play Store URL to search")


# ── Helpers ────────────────────────────────────────────────────────────────────

def resolve_query_to_app_name(query: str) -> Optional[str]:
    """
    Resolves a raw search query (app name OR Play Store URL) to a known app name
    in APP_PERMISSION_DATA.

    Resolution order:
      1. Direct match against APP_PERMISSION_DATA keys (case-insensitive)
      2. Extract package ID from Play Store URL (?id=...) then look up PACKAGE_NAME_MAP
      3. Substring keyword match against PACKAGE_NAME_MAP keys
    """
    query = query.strip()

    # 1. Direct case-insensitive match against known app names
    lower_query = query.lower()
    for key in APP_PERMISSION_DATA:
        if key.lower() == lower_query:
            return key

    # 2. Try to parse as a URL and extract package name
    package_id = None
    try:
        parsed = urlparse(query)
        if parsed.scheme in ("http", "https"):
            params = parse_qs(parsed.query)
            if "id" in params:
                package_id = params["id"][0].lower()  # e.g. "com.whatsapp"
    except Exception:
        pass

    if package_id:
        # 2a. Exact match in PACKAGE_NAME_MAP
        if package_id in PACKAGE_NAME_MAP:
            return PACKAGE_NAME_MAP[package_id]

        # 2b. Substring match — e.g. "com.whatsapp.w4b.something" still matches "whatsapp"
        for keyword, app_name in PACKAGE_NAME_MAP.items():
            if keyword in package_id or package_id in keyword:
                if app_name in APP_PERMISSION_DATA:
                    return app_name

    # 3. Substring keyword match on raw query (handles plain text like "whatsapp")
    for keyword, app_name in PACKAGE_NAME_MAP.items():
        if keyword in lower_query or lower_query in keyword:
            if app_name in APP_PERMISSION_DATA:
                return app_name

    return None


# ── Endpoints ──────────────────────────────────────────────────────────────────

# Search endpoint — resolves app name or Play Store link
@app.post("/search")
def search_app(data: SearchRequest):
    """
    Resolve an app name or Play Store URL and return its risk scan.
    Accepts:
      - Plain app name: "WhatsApp"
      - Play Store URL: https://play.google.com/store/apps/details?id=com.whatsapp&...
    """
    resolved = resolve_query_to_app_name(data.query)

    if not resolved:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find a matching app for: '{data.query}'. "
                   f"Available apps: {sorted(APP_PERMISSION_DATA.keys())}"
        )

    app_data = APP_PERMISSION_DATA[resolved]
    permissions = app_data if isinstance(app_data, list) else app_data.get("declared_permissions", [])
    score, level, explanations = calculate_risk(permissions)

    return {
        "app_name": resolved,
        "resolved_from": data.query,
        "extracted_permissions": permissions,
        "risk_score": score,
        "risk_level": level,
        "explanations": explanations
    }


# Legacy endpoint - Basic scan
@app.post("/scan")
def scan_app(data: AppScanRequest):
    """Legacy endpoint for basic app risk scanning"""
    app_name = data.app_name

    if app_name not in APP_PERMISSION_DATA:
        raise HTTPException(
            status_code=404,
            detail="App not found in extracted metadata database"
        )

    app_data = APP_PERMISSION_DATA[app_name]
    permissions = app_data if isinstance(app_data, list) else app_data.get("declared_permissions", [])
    score, level, explanations = calculate_risk(permissions)

    return {
        "app_name": app_name,
        "extracted_permissions": permissions,
        "risk_score": score,
        "risk_level": level,
        "explanations": explanations
    }


# Comprehensive analysis
@app.post("/analyze")
def analyze_app_comprehensive(data: AppScanRequest):
    """
    Comprehensive app analysis with detailed permission breakdown,
    threat detection, privacy impact, and correlation analysis
    """
    app_name = data.app_name

    if app_name not in APP_PERMISSION_DATA:
        raise HTTPException(status_code=404, detail="App not found in database")

    result = analyze_app(app_name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# Permission analysis
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


# Threat detection
@app.post("/detect-threats")
def detect_threats(data: AppScanRequest):
    """Detect specific threat indicators and suspicious patterns in an app"""
    app_name = data.app_name

    if app_name not in APP_PERMISSION_DATA:
        raise HTTPException(status_code=404, detail="App not found in database")

    analyzer = PermissionAnalyzer()
    threat_indicators = analyzer.detect_threat_indicators(app_name)

    app_data = APP_PERMISSION_DATA[app_name]
    permissions = app_data.get("declared_permissions", []) if isinstance(app_data, dict) else app_data
    correlations = analyzer.detect_permission_correlations(permissions)

    return {
        "app_name": app_name,
        "threat_indicators": threat_indicators,
        "suspicious_patterns": correlations["suspicious_patterns"],
        "pattern_risk_level": correlations["pattern_risk_level"]
    }


# Bulk analysis
@app.post("/bulk-analyze")
def bulk_analyze(data: BulkScanRequest):
    """Analyze multiple apps and return comparative risk summary"""
    results = []

    for app_name in data.app_names:
        if app_name in APP_PERMISSION_DATA:
            result = analyze_app(app_name)
            if "error" not in result:
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


# Permission metadata
@app.get("/permissions")
def get_permissions(category: Optional[str] = None):
    """Get permission metadata with optional category filtering"""
    if category:
        if category not in PERMISSION_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        filtered_perms = {
            p: meta for p, meta in PERMISSION_METADATA.items()
            if meta.get("category") == category
        }
        return {"category": category, "permissions": filtered_perms}
    return PERMISSION_METADATA


# Permission categories
@app.get("/permission-categories")
def get_permission_categories():
    """Get all permission categories and their descriptions"""
    return PERMISSION_CATEGORIES


# Available apps
@app.get("/apps")
def get_available_apps():
    """Get list of all available apps in the database"""
    apps = []
    for app_name, app_data in APP_PERMISSION_DATA.items():
        if isinstance(app_data, dict):
            apps.append({
                "name": app_name,
                "version": app_data.get("version", "Unknown"),
                "risk_level": app_data.get("risk_profile", {}).get("risk_level", "Unknown"),
                "permissions_count": len(app_data.get("declared_permissions", []))
            })
        else:
            apps.append({
                "name": app_name,
                "version": "Unknown",
                "permissions_count": len(app_data)
            })
    return sorted(apps, key=lambda x: x["name"])


# Compare apps
@app.post("/compare")
def compare_apps(data: BulkScanRequest):
    """Compare multiple apps and provide detailed comparison"""
    if len(data.app_names) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 apps to compare")

    analyzer = PermissionAnalyzer()
    apps_data = []

    for app_name in data.app_names:
        if app_name not in APP_PERMISSION_DATA:
            continue
        app_info = APP_PERMISSION_DATA[app_name]
        permissions = app_info.get("declared_permissions", []) if isinstance(app_info, dict) else app_info
        severity = analyzer.calculate_severity_score(permissions)
        apps_data.append({
            "app_name": app_name,
            "risk_score": severity["total_score"],
            "permission_count": len(permissions),
            "dangerous_count": severity["critical_count"] + severity["dangerous_count"],
            "critical_permissions": severity["severity_breakdown"]["critical"]
        })

    if not apps_data:
        raise HTTPException(status_code=404, detail="No valid apps found")

    return {
        "comparison": apps_data,
        "highest_risk": max(apps_data, key=lambda x: x["risk_score"])["app_name"],
        "lowest_risk": min(apps_data, key=lambda x: x["risk_score"])["app_name"]
    }


# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "apps_in_database": len(APP_PERMISSION_DATA),
        "permissions_tracked": len(PERMISSION_METADATA)
    }

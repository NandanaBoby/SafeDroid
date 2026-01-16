from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from risk_engine import calculate_risk, analyze_app, PermissionAnalyzer
from app_data import APP_PERMISSION_DATA, PERMISSION_METADATA, PERMISSION_CATEGORIES

app = FastAPI(title="SafeDroid – App Risk Analyzer", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="frontend")


# Pydantic models
class AppScanRequest(BaseModel):
    app_name: str = Field(..., description="Name of the app to scan")


class PermissionListRequest(BaseModel):
    permissions: List[str] = Field(..., description="List of permission names to analyze")


class BulkScanRequest(BaseModel):
    app_names: List[str] = Field(..., description="List of app names to scan")


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
    
    # Handle both old list format and new dict format
    if isinstance(app_data, list):
        permissions = app_data
    else:
        permissions = app_data.get("declared_permissions", [])
    
    score, level, explanations = calculate_risk(permissions)

    return {
        "app_name": app_name,
        "extracted_permissions": permissions,
        "risk_score": score,
        "risk_level": level,
        "explanations": explanations
    }


# New endpoint - Comprehensive analysis
@app.post("/analyze")
def analyze_app_comprehensive(data: AppScanRequest):
    """
    Comprehensive app analysis with detailed permission breakdown,
    threat detection, privacy impact, and correlation analysis
    """
    app_name = data.app_name

    if app_name not in APP_PERMISSION_DATA:
        raise HTTPException(
            status_code=404,
            detail="App not found in database"
        )

    result = analyze_app(app_name)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# New endpoint - Permission analysis
@app.post("/analyze-permissions")
def analyze_permissions(data: PermissionListRequest):
    """
    Analyze a custom list of permissions for risk assessment
    """
    analyzer = PermissionAnalyzer()
    
    # Validate permissions
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


# New endpoint - Threat detection
@app.post("/detect-threats")
def detect_threats(data: AppScanRequest):
    """
    Detect specific threat indicators and suspicious patterns in an app
    """
    app_name = data.app_name

    if app_name not in APP_PERMISSION_DATA:
        raise HTTPException(
            status_code=404,
            detail="App not found in database"
        )

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


# New endpoint - Bulk analysis
@app.post("/bulk-analyze")
def bulk_analyze(data: BulkScanRequest):
    """
    Analyze multiple apps and return comparative risk summary
    """
    results = []
    
    for app_name in data.app_names:
        if app_name in APP_PERMISSION_DATA:
            result = analyze_app(app_name)
            if "error" not in result:
                results.append(result)
    
    if not results:
        raise HTTPException(status_code=404, detail="No valid apps found")
    
    # Calculate summary statistics
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


# New endpoint - Permission metadata
@app.get("/permissions")
def get_permissions(category: Optional[str] = None):
    """
    Get permission metadata with optional category filtering
    """
    if category:
        if category not in PERMISSION_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        filtered_perms = {
            p: meta for p, meta in PERMISSION_METADATA.items()
            if meta.get("category") == category
        }
        return {
            "category": category,
            "permissions": filtered_perms
        }
    
    return PERMISSION_METADATA


# New endpoint - Permission categories
@app.get("/permission-categories")
def get_permission_categories():
    """
    Get all permission categories and their descriptions
    """
    return PERMISSION_CATEGORIES


# New endpoint - Available apps
@app.get("/apps")
def get_available_apps():
    """
    Get list of all available apps in the database
    """
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


# New endpoint - Compare apps
@app.post("/compare")
def compare_apps(data: BulkScanRequest):
    """
    Compare multiple apps and provide detailed comparison
    """
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


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "apps_in_database": len(APP_PERMISSION_DATA),
        "permissions_tracked": len(PERMISSION_METADATA)
    }

# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from urllib.parse import urlparse, parse_qs
from sqlalchemy.orm import Session

from database import get_db, create_tables, App, AppPermission, PermissionMeta, PackageAlias
from risk_engine import calculate_risk, PermissionAnalyzer
from app_data import PERMISSION_METADATA, PERMISSION_CATEGORIES

create_tables()

app = FastAPI(title="SafeDroid – App Risk Analyzer", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic models ────────────────────────────────────────────────────────────

class AppScanRequest(BaseModel):
    app_name: str = Field(..., description="Name of the app to scan")

class PermissionListRequest(BaseModel):
    permissions: List[str] = Field(..., description="List of permission names to analyze")

class BulkScanRequest(BaseModel):
    app_names: List[str] = Field(..., description="List of app names to scan")

class SearchRequest(BaseModel):
    query: str = Field(..., description="App name or Play Store URL")


# ── Permission normalizer ──────────────────────────────────────────────────────
# Maps every label/description the Play Store scraper returns
# to the PERMISSION_METADATA keys your risk engine understands.

PERMISSION_LABEL_MAP = {
    # Camera
    "camera":                                        "CAMERA",
    "take pictures and videos":                      "CAMERA",
    "android.permission.camera":                     "CAMERA",
    # Microphone
    "microphone":                                    "MICROPHONE",
    "record audio":                                  "MICROPHONE",
    "android.permission.record_audio":               "MICROPHONE",
    # Location
    "location":                                      "ACCESS_FINE_LOCATION",
    "precise location":                              "ACCESS_FINE_LOCATION",
    "gps":                                           "ACCESS_FINE_LOCATION",
    "approximate location":                          "ACCESS_COARSE_LOCATION",
    "network-based location":                        "ACCESS_COARSE_LOCATION",
    "android.permission.access_fine_location":       "ACCESS_FINE_LOCATION",
    "android.permission.access_coarse_location":     "ACCESS_COARSE_LOCATION",
    # Contacts
    "contacts":                                      "READ_CONTACTS",
    "read your contacts":                            "READ_CONTACTS",
    "read contacts":                                 "READ_CONTACTS",
    "modify your contacts":                          "WRITE_CONTACTS",
    "write contacts":                                "WRITE_CONTACTS",
    "android.permission.read_contacts":              "READ_CONTACTS",
    "android.permission.write_contacts":             "WRITE_CONTACTS",
    # SMS
    "sms":                                           "SMS",
    "send sms messages":                             "SEND_SMS",
    "send and view sms messages":                    "SMS",
    "receive text messages":                         "READ_SMS",
    "read your text messages":                       "READ_SMS",
    "read sms":                                      "READ_SMS",
    "android.permission.send_sms":                   "SEND_SMS",
    "android.permission.read_sms":                   "READ_SMS",
    "android.permission.receive_sms":                "READ_SMS",
    # Call log
    "call log":                                      "CALL_LOG",
    "read call log":                                 "READ_CALL_LOG",
    "write call log":                                "WRITE_CALL_LOG",
    "read your call log":                            "READ_CALL_LOG",
    "android.permission.read_call_log":              "READ_CALL_LOG",
    "android.permission.write_call_log":             "WRITE_CALL_LOG",
    # Phone
    "phone":                                         "PHONE_STATE",
    "make and manage phone calls":                   "CALL_PHONE",
    "directly call phone numbers":                   "CALL_PHONE",
    "read phone status and identity":                "PHONE_STATE",
    "android.permission.call_phone":                 "CALL_PHONE",
    "android.permission.read_phone_state":           "PHONE_STATE",
    "android.permission.process_outgoing_calls":     "PROCESS_OUTGOING_CALLS",
    # Storage
    "storage":                                       "READ_EXTERNAL_STORAGE",
    "read the contents of your storage":             "READ_EXTERNAL_STORAGE",
    "read external storage":                         "READ_EXTERNAL_STORAGE",
    "modify or delete the contents of your storage": "WRITE_EXTERNAL_STORAGE",
    "write external storage":                        "WRITE_EXTERNAL_STORAGE",
    "android.permission.read_external_storage":      "READ_EXTERNAL_STORAGE",
    "android.permission.write_external_storage":     "WRITE_EXTERNAL_STORAGE",
    # Calendar
    "calendar":                                      "READ_CALENDAR",
    "read calendar events":                          "READ_CALENDAR",
    "read your calendar":                            "READ_CALENDAR",
    "add or modify calendar events":                 "WRITE_CALENDAR",
    "android.permission.read_calendar":              "READ_CALENDAR",
    "android.permission.write_calendar":             "WRITE_CALENDAR",
    # Accounts
    "accounts":                                      "GET_ACCOUNTS",
    "find accounts on the device":                   "GET_ACCOUNTS",
    "android.permission.get_accounts":               "GET_ACCOUNTS",
    # Sensors
    "body sensors":                                  "SENSORS",
    "sensors":                                       "SENSORS",
    "android.permission.body_sensors":               "SENSORS",
    # Internet
    "internet":                                      "INTERNET",
    "full network access":                           "INTERNET",
    "android.permission.internet":                   "INTERNET",
    # Device admin
    "device admin":                                  "DEVICE_ADMIN",
    "android.permission.bind_device_admin":          "DEVICE_ADMIN",
    # Boot
    "run at startup":                                "RECEIVE_BOOT_COMPLETED",
    "android.permission.receive_boot_completed":     "RECEIVE_BOOT_COMPLETED",
    # Foreground service
    "foreground service":                            "FOREGROUND_SERVICE",
    "android.permission.foreground_service":         "FOREGROUND_SERVICE",
}


def normalize_permissions(raw_permissions: list) -> list:
    """
    Converts raw Play Store permission strings (any format) into
    PERMISSION_METADATA keys the risk engine can score.

    Handles three formats:
      1. Full Android ID:  "android.permission.CAMERA"  -> "CAMERA"
      2. Human label:      "Camera"                     -> "CAMERA"
      3. Already correct:  "CAMERA"                     -> "CAMERA"

    Unknown permissions are kept as-is (listed but score 0).
    """
    normalized = []
    seen = set()

    for raw in raw_permissions:
        if not raw:
            continue

        # 1. Already correct format — exact uppercase match
        upper = raw.upper().replace("ANDROID.PERMISSION.", "")
        if upper in PERMISSION_METADATA and upper not in seen:
            normalized.append(upper)
            seen.add(upper)
            continue

        # 2. Label map lookup (lowercase)
        lower = raw.lower().strip()
        mapped = PERMISSION_LABEL_MAP.get(lower)
        if mapped and mapped not in seen:
            normalized.append(mapped)
            seen.add(mapped)
            continue

        # 3. Strip common prefixes and uppercase
        stripped = (raw
                    .replace("android.permission.", "")
                    .replace("com.google.android.c2dm.permission.", "")
                    .upper())
        if stripped in PERMISSION_METADATA and stripped not in seen:
            normalized.append(stripped)
            seen.add(stripped)
            continue

        # 4. Unknown — keep as-is so it still appears in the list
        if raw not in seen:
            normalized.append(raw)
            seen.add(raw)

    return normalized


# ── Live fetcher ───────────────────────────────────────────────────────────────

def fetch_live_app_data(package_id: str):
    """
    Fetches real permission data for any app from the Play Store.
    Only called when the app is NOT found in the local database.
    Returns a dict with app_name and permissions, or None on failure.
    """
    try:
        from google_play_scraper import app as gplay_app, permissions as gplay_permissions

        result = gplay_app(package_id, lang='en', country='us')

        # Try dedicated permissions endpoint first (more complete)
        try:
            perm_data = gplay_permissions(package_id, lang='en', country='us')
            raw_list = []
            if isinstance(perm_data, dict):
                for group_perms in perm_data.values():
                    if isinstance(group_perms, list):
                        raw_list.extend(group_perms)
            elif isinstance(perm_data, list):
                raw_list = perm_data
        except Exception:
            raw_list = result.get("permissions", []) or []

        normalized = normalize_permissions(raw_list)

        return {
            "app_name":    result.get("title", package_id),
            "package_id":  package_id,
            "permissions": normalized,
            "developer":   result.get("developer", "Unknown"),
            "category":    result.get("genre", "Unknown"),
            "version":     result.get("version", "Unknown"),
            "installs":    result.get("installs", "Unknown")
        }

    except ImportError:
        return None
    except Exception:
        return None


def save_live_app_to_db(live_data: dict, db: Session):
    """Saves a live-fetched app into the DB for future searches."""
    try:
        existing = db.query(App).filter(App.name.ilike(live_data["app_name"])).first()
        if existing:
            return existing.name

        app_row = App(
            name      = live_data["app_name"],
            version   = live_data.get("version", "Unknown"),
            category  = live_data.get("category", "Unknown"),
            developer = live_data.get("developer", "Unknown")
        )
        db.add(app_row)
        db.flush()

        for perm in live_data["permissions"]:
            db.add(AppPermission(app_id=app_row.id, permission_name=perm))

        db.add(PackageAlias(app_id=app_row.id, package_id=live_data["package_id"].lower()))

        db.commit()
        return app_row.name

    except Exception:
        db.rollback()
        return live_data["app_name"]


# ── DB Helpers ─────────────────────────────────────────────────────────────────

def get_app_permissions_from_db(app_name: str, db: Session):
    app_row = db.query(App).filter(App.name.ilike(app_name)).first()
    if not app_row:
        return None
    return [p.permission_name for p in app_row.permissions]


def extract_package_id(query: str):
    """Extract package ID from a Play Store URL or plain package name."""
    query = query.strip()
    try:
        parsed = urlparse(query)
        if parsed.scheme in ("http", "https"):
            params = parse_qs(parsed.query)
            if "id" in params:
                return params["id"][0].lower()
    except Exception:
        pass
    if "." in query and " " not in query and "://" not in query:
        return query.lower()
    return None


def guess_package_ids(app_name: str) -> list:
    """
    Given a plain app name like "Snapchat" or "Google Maps",
    generates a list of likely package IDs to try against the Play Store.

    Most Android apps follow predictable naming patterns:
      - com.snapchat.android
      - com.google.android.apps.maps
      - com.appname (most common simple pattern)

    We try multiple guesses in order of likelihood.
    """
    name   = app_name.strip().lower()
    # Remove spaces and special characters for package name use
    clean  = name.replace(" ", "").replace("-", "").replace("_", "")
    # For multi-word names, also try joined words
    words  = name.split()
    first  = words[0] if words else clean

    candidates = []

    # Most common pattern: com.appname.android
    candidates.append(f"com.{clean}.android")
    # Simple: com.appname
    candidates.append(f"com.{clean}")
    # Google pattern for google-made apps
    if "google" in name or words[0] == "google" and len(words) > 1:
        candidates.append(f"com.google.android.apps.{words[-1]}")
        candidates.append(f"com.google.android.{words[-1]}")
    # Meta/Facebook pattern
    if any(w in name for w in ["facebook", "instagram", "whatsapp", "messenger"]):
        candidates.append(f"com.{first}")
    # Two-word apps: com.word1.word2
    if len(words) >= 2:
        candidates.append(f"com.{words[0]}.{words[1]}")
    # Try with just the first word
    candidates.append(f"com.{first}.android")
    candidates.append(f"com.{first}")

    # Deduplicate while preserving order
    seen = set()
    result = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result


def resolve_query_to_app_name(query: str, db: Session):
    query = query.strip()

    # 1. Direct name match
    app_row = db.query(App).filter(App.name.ilike(query)).first()
    if app_row:
        return app_row.name

    # 2. Package alias lookup
    package_id = extract_package_id(query)
    if package_id:
        alias = db.query(PackageAlias).filter(PackageAlias.package_id == package_id).first()
        if alias:
            return alias.app.name
        alias = db.query(PackageAlias).filter(PackageAlias.package_id.contains(package_id)).first()
        if alias:
            return alias.app.name

    # 3. Keyword match against all saved aliases
    lower_q = query.lower()
    for alias in db.query(PackageAlias).all():
        if lower_q in alias.package_id or alias.package_id in lower_q:
            return alias.app.name

    return None


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        from google_play_scraper import app as _
        scraper_status = "installed ✓"
    except ImportError:
        scraper_status = "not installed (live fetch disabled)"

    return {
        "status": "healthy",
        "version": "3.1.0",
        "database": "connected ✓",
        "apps_in_database": db.query(App).count(),
        "permissions_tracked": db.query(PermissionMeta).count(),
        "live_scraper": scraper_status
    }


@app.get("/apps")
def get_available_apps(db: Session = Depends(get_db)):
    apps = db.query(App).order_by(App.name).all()
    return [{"name": a.name, "version": a.version or "Unknown", "permissions_count": len(a.permissions)} for a in apps]


@app.post("/search")
def search_app(data: SearchRequest, db: Session = Depends(get_db)):
    """
    Search by app name or Play Store URL.
    1. Check local DB first (fast)
    2. If not found, fetch live from Play Store and save to DB
    """
    source = "database"

    resolved = resolve_query_to_app_name(data.query, db)

    if not resolved:
        package_id = extract_package_id(data.query)
        live_data  = None

        if package_id:
            # It was a URL or dotted package name — try directly
            live_data = fetch_live_app_data(package_id)
        else:
            # It's a plain app name like "Snapchat" or "Google Maps"
            # Generate candidate package IDs and try each one
            candidates = guess_package_ids(data.query)
            for candidate in candidates:
                live_data = fetch_live_app_data(candidate)
                if live_data:
                    break  # found it — stop trying

        if live_data:
            resolved = save_live_app_to_db(live_data, db)
            source   = "live_fetch"
        else:
            available = [a.name for a in db.query(App).order_by(App.name).all()]
            raise HTTPException(status_code=404, detail={
                "message": f"Could not find '{data.query}'. Try pasting the Play Store link directly for best results.",
                "tip": "e.g. https://play.google.com/store/apps/details?id=com.snapchat.android",
                "available_apps": available
            })

    permissions = get_app_permissions_from_db(resolved, db)
    score, level, explanations = calculate_risk(permissions)

    return {
        "app_name":              resolved,
        "resolved_from":         data.query,
        "extracted_permissions": permissions,
        "risk_score":            score,
        "risk_level":            level,
        "explanations":          explanations,
        "source":                source
    }


@app.post("/scan")
def scan_app(data: AppScanRequest, db: Session = Depends(get_db)):
    permissions = get_app_permissions_from_db(data.app_name, db)
    if permissions is None:
        available = [a.name for a in db.query(App).order_by(App.name).all()]
        raise HTTPException(status_code=404, detail=f"App not found. Available: {available}")

    score, level, explanations = calculate_risk(permissions)
    return {
        "app_name":              data.app_name,
        "extracted_permissions": permissions,
        "risk_score":            score,
        "risk_level":            level,
        "explanations":          explanations,
        "source":                "database"
    }


@app.post("/analyze")
def analyze_app_endpoint(data: AppScanRequest, db: Session = Depends(get_db)):
    permissions = get_app_permissions_from_db(data.app_name, db)
    if permissions is None:
        raise HTTPException(status_code=404, detail="App not found in database")

    analyzer             = PermissionAnalyzer()
    severity_analysis    = analyzer.calculate_severity_score(permissions)
    correlation_analysis = analyzer.detect_permission_correlations(permissions)
    privacy_analysis     = analyzer.analyze_privacy_impact(permissions)
    categorized          = analyzer.categorize_permissions(permissions)
    total_score          = severity_analysis["total_score"]
    risk_level           = analyzer.calculate_risk_level(total_score)

    return {
        "app_name":   data.app_name,
        "risk_score": total_score,
        "risk_level": risk_level,
        "permission_analysis": {
            "total_declared":     len(permissions),
            "severity_breakdown": severity_analysis["severity_breakdown"],
            "category_scores":    severity_analysis["category_scores"]
        },
        "privacy_analysis":        privacy_analysis,
        "categorized_permissions": categorized,
        "correlation_analysis":    correlation_analysis,
        "source": "database"
    }


@app.post("/detect-threats")
def detect_threats(data: AppScanRequest, db: Session = Depends(get_db)):
    permissions = get_app_permissions_from_db(data.app_name, db)
    if permissions is None:
        raise HTTPException(status_code=404, detail="App not found in database")

    analyzer     = PermissionAnalyzer()
    correlations = analyzer.detect_permission_correlations(permissions)
    indicators   = {
        "privilege_escalation":   "DEVICE_ADMIN" in permissions,
        "data_exfiltration_risk": "CRITICAL" if len(permissions) > 15 else "HIGH" if len(permissions) > 10 else "MEDIUM",
        "financial_risk":         "HIGH" if ("SEND_SMS" in permissions or "CALL_PHONE" in permissions) else "LOW",
        "detected_threats":       correlations["suspicious_patterns"]
    }
    return {
        "app_name":            data.app_name,
        "threat_indicators":   indicators,
        "suspicious_patterns": correlations["suspicious_patterns"],
        "pattern_risk_level":  correlations["pattern_risk_level"],
        "source":              "database"
    }


@app.post("/bulk-analyze")
def bulk_analyze(data: BulkScanRequest, db: Session = Depends(get_db)):
    results  = []
    analyzer = PermissionAnalyzer()
    for app_name in data.app_names:
        permissions = get_app_permissions_from_db(app_name, db)
        if permissions is not None:
            severity   = analyzer.calculate_severity_score(permissions)
            risk_level = analyzer.calculate_risk_level(severity["total_score"])
            results.append({"app_name": app_name, "risk_score": severity["total_score"], "risk_level": risk_level, "permission_count": len(permissions)})

    if not results:
        raise HTTPException(status_code=404, detail="No valid apps found")

    avg_score   = sum(r["risk_score"] for r in results) / len(results)
    risk_levels = [r["risk_level"] for r in results]
    return {
        "total_apps_analyzed": len(results),
        "average_risk_score":  round(avg_score, 2),
        "risk_level_distribution": {"CRITICAL": risk_levels.count("CRITICAL"), "HIGH": risk_levels.count("HIGH"), "MEDIUM": risk_levels.count("MEDIUM"), "LOW": risk_levels.count("LOW")},
        "apps":   results,
        "source": "database"
    }


@app.post("/compare")
def compare_apps(data: BulkScanRequest, db: Session = Depends(get_db)):
    if len(data.app_names) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 apps")

    analyzer  = PermissionAnalyzer()
    apps_data = []
    for app_name in data.app_names:
        permissions = get_app_permissions_from_db(app_name, db)
        if permissions:
            severity = analyzer.calculate_severity_score(permissions)
            apps_data.append({"app_name": app_name, "risk_score": severity["total_score"], "permission_count": len(permissions), "dangerous_count": severity["critical_count"] + severity["dangerous_count"]})

    if not apps_data:
        raise HTTPException(status_code=404, detail="No valid apps found")

    return {
        "comparison":   apps_data,
        "highest_risk": max(apps_data, key=lambda x: x["risk_score"])["app_name"],
        "lowest_risk":  min(apps_data, key=lambda x: x["risk_score"])["app_name"],
        "source":       "database"
    }


@app.get("/permissions")
def get_permissions(category: Optional[str] = None):
    if category:
        if category not in PERMISSION_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        filtered = {p: m for p, m in PERMISSION_METADATA.items() if m.get("category") == category}
        return {"category": category, "permissions": filtered}
    return PERMISSION_METADATA


@app.get("/permission-categories")
def get_permission_categories():
    return PERMISSION_CATEGORIES

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from risk_engine import calculate_risk
from app_data import APP_PERMISSION_DATA

app = FastAPI(title="SafeDroid – App Risk Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="frontend")



class AppScanRequest(BaseModel):
    app_name: str

@app.post("/scan")
def scan_app(data: AppScanRequest):
    app_name = data.app_name

    if app_name not in APP_PERMISSION_DATA:
        raise HTTPException(
            status_code=404,
            detail="App not found in extracted metadata database"
        )

    permissions = APP_PERMISSION_DATA[app_name]
    score, level, explanations = calculate_risk(permissions)

    return {
        "app_name": app_name,
        "extracted_permissions": permissions,
        "risk_score": score,
        "risk_level": level,
        "explanations": explanations
    }

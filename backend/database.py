"""
Database configuration and models for SafeDroid
Uses PostgreSQL for persistent storage
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
# attempt to pull the richer data set first, fall back to the smaller
# app_data module for compatibility.  main.py already does the same, so
# keep the behaviour consistent across the backend.
# package-qualified data imports to support running from root
# relative data imports ensure the module works regardless of cwd
# we also fall back to bare-module imports when not part of a package
try:
    from .app_data_full import (
        PERMISSION_METADATA,
        PERMISSION_CATEGORIES,
        APP_PERMISSION_DATA,
        PERMISSION_CORRELATIONS,
        RISK_THRESHOLDS,
        TRUSTED_PUBLISHERS,
        PACKAGE_NAME_MAP
    )
except ImportError:
    try:
        from .app_data import (
            PERMISSION_METADATA,
            PERMISSION_CATEGORIES,
            APP_PERMISSION_DATA,
            PERMISSION_CORRELATIONS,
            RISK_THRESHOLDS,
            TRUSTED_PUBLISHERS,
            PACKAGE_NAME_MAP
        )
    except ImportError:
        # likely running directly from backend directory
        from app_data_full import (
            PERMISSION_METADATA,
            PERMISSION_CATEGORIES,
            APP_PERMISSION_DATA,
            PERMISSION_CORRELATIONS,
            RISK_THRESHOLDS,
            TRUSTED_PUBLISHERS,
            PACKAGE_NAME_MAP
        )

# Database URL can be overridden via environment variable for
# portability/testing.  defaults to PostgreSQL but falls back to a
# local sqlite file if not specified.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/safedroid")
# for simple local development where postgres isn't available use
# DATABASE_URL=sqlite:///./safedroid.db

# Create engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class App(Base):
    """App model storing app information and permissions"""
    __tablename__ = "apps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    version = Column(String, default="Unknown")
    risk_score = Column(Integer, default=0)
    risk_level = Column(String, default="UNKNOWN")
    permissions = Column(JSON, default=list)
    package_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    risk_profile = relationship("RiskProfile", back_populates="app", uselist=False)
    permission_justifications = relationship("PermissionJustification", back_populates="app")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "permissions": self.permissions,
            "package_name": self.package_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class RiskProfile(Base):
    """Risk profile for each app"""
    __tablename__ = "risk_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), unique=True)
    data_exfiltration_risk = Column(String, default="LOW")
    financial_risk = Column(String, default="LOW")
    privacy_risk = Column(String, default="LOW")
    privilege_escalation = Column(Boolean, default=False)
    detected_threats = Column(JSON, default=list)
    
    app = relationship("App", back_populates="risk_profile")


class PermissionJustification(Base):
    """Permission justifications for apps"""
    __tablename__ = "permission_justifications"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"))
    permission = Column(String)
    justification = Column(String)
    
    app = relationship("App", back_populates="permission_justifications")


# Database helper functions
def get_db():
    """Yield a database session and ensure it always closes.

    The previous implementation attempted to close twice when an
    exception was raised; the extra handling wasn't necessary and made
    the control flow harder to follow. This version relies on the
    finally block only.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def seed_database():
    """Seed database with initial app data from APP_PERMISSION_DATA.

    The hard‑coded dictionary previously duplicated the contents of
    app_data/app_data_full.  We now iterate over the imported
    ``APP_PERMISSION_DATA`` so additions made in the data files are
    automatically propagated, and we close the session regardless of
    whether seeding succeeds.
    """
    try:
        from .risk_engine import calculate_risk
    except ImportError:
        # when running as script in backend folder
        from risk_engine import calculate_risk

    db = SessionLocal()
    try:
        # check if already seeded
        existing_apps = db.query(App).count()
        if existing_apps > 0:
            print(f"Database already has {existing_apps} apps. Skipping seed.")
            return

        # Build seed data from the imported constant; it may contain either a
        # list of permissions or a dict with metadata, depending on the
        # version of the data file.
        for app_name, data in APP_PERMISSION_DATA.items():
            if isinstance(data, dict):
                permissions = data.get("declared_permissions", []) or data.get("permissions", [])
                version = data.get("version", "Unknown")
                package_name = data.get("package_name")
            else:
                permissions = data
                version = "Unknown"
                package_name = None

            score, level, explanations = calculate_risk(permissions)
            app = App(
                name=app_name,
                version=version,
                risk_score=score,
                risk_level=level,
                permissions=permissions,
                package_name=package_name
            )
            db.add(app)

        db.commit()
        print(f"Successfully seeded {len(APP_PERMISSION_DATA)} apps to database!")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

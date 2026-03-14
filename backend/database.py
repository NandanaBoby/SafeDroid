# database.py
"""
Database connection and table setup for SafeDroid.
Uses SQLite via SQLAlchemy — no external server needed.
The database file (safedroid.db) is auto-created in the backend folder.
"""

from sqlalchemy import (
    create_engine, Column, String, Integer, 
    Text, Boolean, Float, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# SQLite file will be created at backend/safedroid.db
DATABASE_URL = "sqlite:///./safedroid.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite + FastAPI
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


# ── Tables ─────────────────────────────────────────────────────────────────────

class App(Base):
    """One row per app in the dataset"""
    __tablename__ = "apps"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, unique=True, index=True, nullable=False)
    version     = Column(String, default="Unknown")
    category    = Column(String, default="Unknown")
    developer   = Column(String, default="Unknown")

    # Relationships
    permissions = relationship("AppPermission", back_populates="app", cascade="all, delete-orphan")
    package_ids = relationship("PackageAlias",  back_populates="app", cascade="all, delete-orphan")


class AppPermission(Base):
    """Permissions belonging to each app (one row per permission per app)"""
    __tablename__ = "app_permissions"

    id              = Column(Integer, primary_key=True, index=True)
    app_id          = Column(Integer, ForeignKey("apps.id"), nullable=False)
    permission_name = Column(String, nullable=False)

    app = relationship("App", back_populates="permissions")


class PermissionMeta(Base):
    """Metadata for each known permission"""
    __tablename__ = "permission_meta"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, unique=True, index=True, nullable=False)
    category        = Column(String)
    risk_level      = Column(String)
    severity        = Column(Integer, default=1)
    description     = Column(Text)
    privacy_impact  = Column(String, default="LOW")
    can_access      = Column(Text)   # stored as comma-separated string
    dangerous       = Column(Boolean, default=False)


class PackageAlias(Base):
    """
    Maps Play Store package IDs to app names.
    e.g. com.whatsapp → WhatsApp
    """
    __tablename__ = "package_aliases"

    id          = Column(Integer, primary_key=True, index=True)
    app_id      = Column(Integer, ForeignKey("apps.id"), nullable=False)
    package_id  = Column(String, unique=True, index=True, nullable=False)

    app = relationship("App", back_populates="package_ids")


# ── Helpers ────────────────────────────────────────────────────────────────────

def create_tables():
    """Create all tables if they don't exist yet"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    FastAPI dependency — yields a DB session per request and closes it after.
    Usage in endpoint:  db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

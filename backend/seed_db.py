# seed_db.py
"""
Run this ONCE to populate the SQLite database with demo data.
Command: python seed_db.py

Safe to re-run — it checks before inserting to avoid duplicates.
"""

from database import create_tables, SessionLocal
from database import App, AppPermission, PermissionMeta, PackageAlias
from app_data import PERMISSION_METADATA, APP_PERMISSION_DATA, PACKAGE_NAME_MAP

def seed():
    create_tables()
    db = SessionLocal()

    try:
        print("📦 Seeding permission metadata...")
        for perm_name, meta in PERMISSION_METADATA.items():
            exists = db.query(PermissionMeta).filter_by(name=perm_name).first()
            if not exists:
                can_access_str = ", ".join(meta.get("can_access", []))
                db.add(PermissionMeta(
                    name           = perm_name,
                    category       = meta.get("category", "UNKNOWN"),
                    risk_level     = meta.get("risk_level", "NORMAL"),
                    severity       = meta.get("severity", 1),
                    description    = meta.get("description", ""),
                    privacy_impact = meta.get("privacy_impact", "LOW"),
                    can_access     = can_access_str,
                    dangerous      = meta.get("dangerous", False)
                ))
        db.commit()
        print(f"   ✓ {len(PERMISSION_METADATA)} permissions seeded")

        print("\n📱 Seeding apps...")
        for app_name, permissions in APP_PERMISSION_DATA.items():
            exists = db.query(App).filter_by(name=app_name).first()
            if not exists:
                app_row = App(name=app_name)
                db.add(app_row)
                db.flush()  # get the new app's ID

                perm_list = permissions if isinstance(permissions, list) else permissions.get("declared_permissions", [])
                for perm_name in perm_list:
                    db.add(AppPermission(
                        app_id=app_row.id,
                        permission_name=perm_name
                    ))
                print(f"   ✓ {app_name} — {len(perm_list)} permissions")

        db.commit()

        print("\n🔗 Seeding package aliases...")
        for package_id, app_name in PACKAGE_NAME_MAP.items():
            app_row = db.query(App).filter_by(name=app_name).first()
            if app_row:
                exists = db.query(PackageAlias).filter_by(package_id=package_id).first()
                if not exists:
                    db.add(PackageAlias(
                        app_id=app_row.id,
                        package_id=package_id
                    ))
        db.commit()
        print(f"   ✓ {len(PACKAGE_NAME_MAP)} aliases seeded")

        print("\n✅ Database seeded successfully → safedroid.db")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

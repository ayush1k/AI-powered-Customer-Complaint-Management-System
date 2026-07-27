import os
import sys

# Ensure both project root and backend directory are in sys.path
db_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(db_dir)
backend_dir = os.path.dirname(app_dir)
project_root = os.path.dirname(backend_dir)

for path in [project_root, backend_dir]:
    if path and path not in sys.path:
        sys.path.insert(0, path)

try:
    from backend.app.db.session import engine, SessionLocal, Base
    from backend.app.db.models import Complaint
except ImportError:
    from app.db.session import engine, SessionLocal, Base
    from app.db.models import Complaint


def init_db(seed_data: bool = True):
    """
    Initialize database tables and optionally populate initial seed data.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

    if seed_data:
        db = SessionLocal()
        try:
            count = db.query(Complaint).count()
            if count == 0:
                print("Seeding initial complaint record...")
                sample_complaint = Complaint(
                    complaint_id="CMP-2026-0001",
                    product_name="CardioShield",
                    strength="10mg",
                    batch_number="LOT-9921A",
                    manufacture_date="2025-01-15",
                    expiry_date="2027-11-30",
                    complaint_quantity="15 bottles",
                    description="Black specks observed inside sealed blister foil. Patient experienced mild nausea.",
                    complainant_name="Dr. Sarah Jenkins",
                    complainant_role="Pharmacist",
                    complainant_contact="s.jenkins@stjudehospital.org",
                    defect_category="Contamination / Discoloration",
                    status="IN_REVIEW",
                    severity="Major",
                    risk_justification="Particulate contamination in unit dose tablets.",
                    recommended_actions=[
                        "Quarantine lot LOT-9921A",
                        "File FDA Alert Report",
                        "Inspect retention samples",
                    ],
                    risk_score=78,
                    health_hazard_class="CLASS_II",
                    regulatory_reportable=True,
                    reporting_deadline_days=15,
                )
                db.add(sample_complaint)
                db.commit()
                db.refresh(sample_complaint)
                print(f"Seeded sample complaint record with ID: {sample_complaint.complaint_id}")
            else:
                print(f"Database already contains {count} complaint records.")
        finally:
            db.close()


if __name__ == "__main__":
    init_db()

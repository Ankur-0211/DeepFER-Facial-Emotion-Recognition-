import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.db.models import ModelVersion

db = SessionLocal()
existing = db.query(ModelVersion).filter_by(version_tag="v1").first()
if not existing:
    db.add(
        ModelVersion(
            version_tag="v1",
            test_accuracy=0.6195,
            artifact_path="ml/inference/artifacts/best_model.keras",
            is_active=True,
        )
    )
    db.commit()
    print("Registered model v1 (test_accuracy=0.6195)")
else:
    print("v1 already registered")
db.close()
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    version_tag: Mapped[str] = mapped_column(String(50), unique=True)
    trained_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    test_accuracy: Mapped[float] = mapped_column(Float)
    artifact_path: Mapped[str] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
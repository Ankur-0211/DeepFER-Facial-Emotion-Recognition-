from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    model_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True
    )
    source_type: Mapped[str] = mapped_column(String(20))  # "image" | "video" | "stream"
    emotion_label: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    user = relationship("User", back_populates="predictions")
    details = relationship(
        "PredictionDetail", back_populates="prediction", cascade="all, delete-orphan"
    )


class PredictionDetail(Base):
    __tablename__ = "prediction_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id", ondelete="CASCADE")
    )
    bounding_box: Mapped[dict] = mapped_column(JSON)
    class_probabilities: Mapped[dict] = mapped_column(JSON)

    prediction = relationship("Prediction", back_populates="details")
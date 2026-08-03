from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models import Prediction, User
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/summary")
def reports_summary(
    db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    rows = db.execute(
        select(Prediction.emotion_label, func.count(Prediction.id))
        .where(Prediction.user_id == current_user.id)
        .group_by(Prediction.emotion_label)
    ).all()
    return {"distribution": [{"emotion": label, "count": count} for label, count in rows]}
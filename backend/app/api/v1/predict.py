import os
import tempfile

import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Prediction, PredictionDetail, ModelVersion, User
from app.core.deps import get_current_user
from app.services.inference_client import predict_faces_async
from app.schemas.predict import PredictionResponseSchema, FacePrediction, BoundingBoxSchema

router = APIRouter(prefix="/api/v1/predict", tags=["predict"])


def _active_model_version_id(db: DBSession) -> int | None:
    version = db.scalar(select(ModelVersion).where(ModelVersion.is_active.is_(True)))
    return version.id if version else None


@router.post("/image", response_model=PredictionResponseSchema)
async def predict_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image")

    faces = await predict_faces_async(image)
    if not faces:
        return PredictionResponseSchema(predictions=[])

    primary = max(faces, key=lambda f: f["confidence"])
    prediction = Prediction(
        user_id=current_user.id,
        model_version_id=_active_model_version_id(db),
        source_type="image",
        emotion_label=primary["label"],
        confidence=primary["confidence"],
    )
    db.add(prediction)
    db.flush()  # assigns prediction.id without committing yet

    for face in faces:
        db.add(
            PredictionDetail(
                prediction_id=prediction.id,
                bounding_box=face["bounding_box"],
                class_probabilities=face["class_probabilities"],
            )
        )
    db.commit()

    return PredictionResponseSchema(
        predictions=[
            FacePrediction(
                emotion=f["label"],
                confidence=f["confidence"],
                boundingBox=BoundingBoxSchema(**f["bounding_box"]),
            )
            for f in faces
        ]
    )

@router.post("/video")
async def predict_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    timeline = []
    try:
        cap = cv2.VideoCapture(tmp_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        sample_every_n = max(int(fps), 1)  # ~1 sample per second of video
        model_version_id = _active_model_version_id(db)
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % sample_every_n == 0:
                faces = await predict_faces_async(frame)
                if faces:
                    primary = max(faces, key=lambda f: f["confidence"])
                    timeline.append(
                        {
                            "timestamp_sec": round(frame_idx / fps, 2),
                            "emotion": primary["label"],
                            "confidence": primary["confidence"],
                        }
                    )
                    prediction = Prediction(
                        user_id=current_user.id,
                        model_version_id=model_version_id,
                        source_type="video",
                        emotion_label=primary["label"],
                        confidence=primary["confidence"],
                    )
                    db.add(prediction)
                    db.flush()
                    for face in faces:
                        db.add(
                            PredictionDetail(
                                prediction_id=prediction.id,
                                bounding_box=face["bounding_box"],
                                class_probabilities=face["class_probabilities"],
                            )
                        )
            frame_idx += 1
        cap.release()
        db.commit()
    finally:
        os.unlink(tmp_path)

    return {"timeline": timeline}
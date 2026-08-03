import numpy as np
import cv2
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.security import decode_token
from app.services.inference_client import predict_faces_async
from app.schemas.predict import BoundingBoxSchema

router = APIRouter()


@router.websocket("/ws/v1/stream")
async def stream_predictions(websocket: WebSocket, token: str = Query(...)):
    try:
        decode_token(token)
    except Exception:
        await websocket.close(code=4401)  # custom close code = auth failure
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            np_arr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                await websocket.send_json({"error": "invalid frame"})
                continue
            faces = await predict_faces_async(frame)
            await websocket.send_json(
                {
                    "predictions": [
                        {
                            "emotion": f["label"],
                            "confidence": f["confidence"],
                            "boundingBox": BoundingBoxSchema(
                                x=f["bounding_box"][0],
                                y=f["bounding_box"][1],
                                width=f["bounding_box"][2],
                                height=f["bounding_box"][3],
                            ).model_dump(),
                        }
                        for f in faces
                    ]
                }
            )
    except WebSocketDisconnect:
        pass
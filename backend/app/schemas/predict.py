from pydantic import BaseModel


class BoundingBoxSchema(BaseModel):
    x: int
    y: int
    width: int
    height: int


class FacePrediction(BaseModel):
    emotion: str
    confidence: float
    boundingBox: BoundingBoxSchema


class PredictionResponseSchema(BaseModel):
    predictions: list[FacePrediction]
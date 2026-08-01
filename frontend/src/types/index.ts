export type Emotion =
  | "angry" | "disgust" | "fear" | "happy" | "sad" | "surprise" | "neutral";

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface EmotionPrediction {
  emotion: Emotion;
  confidence: number;
  boundingBox: BoundingBox;
}

export interface PredictionResponse {
  predictions: EmotionPrediction[];
  timestamp: string;
}

export interface User {
  email: string;
  role: "user" | "admin";
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
import axios from "axios";
import type { PredictionResponse, AuthTokens, User, VideoPredictionResponse } from "../types";
import { getAccessToken } from "./tokenStore";


export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE_URL });

client.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(email: string, password: string): Promise<AuthTokens> {
  const { data } = await client.post<AuthTokens>("/api/v1/auth/login", { email, password });
  return data;
}

export async function register(email: string, password: string): Promise<User> {
  const { data } = await client.post<User>("/api/v1/auth/register", { email, password });
  return data;
}

export async function predictImage(file: File): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await client.post<{ predictions: PredictionResponse["predictions"] }>(
    "/api/v1/predict/image",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return { predictions: data.predictions, timestamp: new Date().toISOString() };
}

export async function predictVideo(file: File): Promise<VideoPredictionResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await client.post<VideoPredictionResponse>(
    "/api/v1/predict/video",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}

export async function fetchReportsSummary(): Promise<{ emotion: string; count: number }[]> {
  const { data } = await client.get<{ distribution: { emotion: string; count: number }[] }>(
    "/api/v1/reports/summary"
  );
  return data.distribution;
}
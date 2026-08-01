import type { PredictionResponse, AuthTokens, User } from "../types";

// NOTE: This is a mock client for Phase 4 UI development.
// Phase 6 replaces the bodies of these functions with real axios calls
// against the FastAPI backend from Phases 2-3.

const MOCK_DELAY = 500;

function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), MOCK_DELAY));
}

export async function login(email: string, _password: string): Promise<AuthTokens> {
  return delay({
    access_token: "mock-access-token",
    refresh_token: "mock-refresh-token",
    token_type: "bearer",
  });
}

export async function register(email: string, _password: string): Promise<User> {
  return delay({ email, role: "user" });
}

export async function predictImage(_file: File): Promise<PredictionResponse> {
  return delay({
    predictions: [
      {
        emotion: "happy",
        confidence: 0.92,
        boundingBox: { x: 50, y: 40, width: 120, height: 120 },
      },
    ],
    timestamp: new Date().toISOString(),
  });
}
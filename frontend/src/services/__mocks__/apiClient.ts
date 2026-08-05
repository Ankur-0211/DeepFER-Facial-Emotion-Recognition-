import type {
  AuthTokens,
  User,
  PredictionResponse,
  VideoPredictionResponse,
} from "../../types";

export const API_BASE_URL = "http://localhost:8000";

export const login: jest.Mock<Promise<AuthTokens>, [string, string]> = jest.fn();
export const register: jest.Mock<Promise<User>, [string, string]> = jest.fn();
export const predictImage: jest.Mock<Promise<PredictionResponse>, [File]> = jest.fn();
export const predictVideo: jest.Mock<Promise<VideoPredictionResponse>, [File]> = jest.fn();
export const fetchReportsSummary: jest.Mock<Promise<{ emotion: string; count: number }[]>, []> = jest.fn();
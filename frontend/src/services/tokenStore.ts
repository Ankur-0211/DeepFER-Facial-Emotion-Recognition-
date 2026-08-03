const STORAGE_KEY = "deepfer_access_token";

let accessToken: string | null = localStorage.getItem(STORAGE_KEY);

export function setAccessToken(token: string | null) {
  accessToken = token;
  if (token) {
    localStorage.setItem(STORAGE_KEY, token);
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export function getAccessToken(): string | null {
  return accessToken;
}
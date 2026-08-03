import { useState, type ChangeEvent } from "react";
import * as api from "../services/apiClient";
import type { PredictionResponse } from "../types";

export default function UploadPanel() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await api.predictImage(file);
      setResult(response);
    } catch (err: any) {
      const status = err?.response?.status;
      if (status === 401) {
        setError("Your session expired — please log in again.");
      } else {
        setError("Something went wrong analyzing this image. Check the console for details.");
      }
      console.error("predictImage failed:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border rounded-xl p-6 bg-white shadow-sm">
      <label className="sr-only" htmlFor="image-upload">Upload an image</label>
      <h2 className="text-lg font-medium text-slate-800 mb-3">Upload an image</h2>
      <input id="image-upload" type="file" accept="image/*" onChange={handleFileChange} />
      {loading && <p className="text-slate-500 mt-3">Analyzing…</p>}
      {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
      {result && (
        <ul className="mt-3">
          {result.predictions.map((p, i) => (
            <li key={i} className="text-slate-700">
              {p.emotion} — {(p.confidence * 100).toFixed(0)}% confidence
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
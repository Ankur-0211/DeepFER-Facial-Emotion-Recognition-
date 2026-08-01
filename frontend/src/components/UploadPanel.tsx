import { useState, type ChangeEvent } from "react";
import * as api from "../services/apiClient";
import type { PredictionResponse } from "../types";

export default function UploadPanel() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    const response = await api.predictImage(file);
    setResult(response);
    setLoading(false);
  }

  return (
    <div className="border rounded-xl p-6 bg-white shadow-sm">
      <h2 className="text-lg font-medium text-slate-800 mb-3">Upload an image</h2>
      <label htmlFor="image-upload" className="sr-only">Upload an image</label>
      <input  type="file" id="image-upload" accept="image/*" onChange={handleFileChange} />
      {loading && <p className="text-slate-500 mt-3">Analyzing…</p>}
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
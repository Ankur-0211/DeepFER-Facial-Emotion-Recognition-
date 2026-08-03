import { useState, type ChangeEvent } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import * as api from "../services/apiClient";
import type { VideoPredictionResponse } from "../types";

export default function VideoUploadPanel() {
  const [result, setResult] = useState<VideoPredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await api.predictVideo(file);
      setResult(response);
    } catch (err: any) {
      const status = err?.response?.status;
      if (status === 401) {
        setError("Your session expired — please log in again.");
      } else {
        setError("Something went wrong analyzing this video. Check the console for details.");
      }
      console.error("predictVideo failed:", err);
    } finally {
      setLoading(false);
    }
  }

  // Recharts needs a numeric y-value per point; map emotion labels to a
  // fixed order so the line has a meaningful vertical position per emotion.
  const emotionOrder = ["angry", "disgust", "fear", "sad", "neutral", "surprise", "happy"];
  const chartData = result?.timeline.map((entry) => ({
    ...entry,
    emotionIndex: emotionOrder.indexOf(entry.emotion),
  }));

  return (
    <div className="border rounded-xl p-6 bg-white shadow-sm">
      <label className="sr-only" htmlFor="video-upload">Upload a video</label>
      <h2 className="text-lg font-medium text-slate-800 mb-3">Upload a video</h2>
      <input id="video-upload" type="file" accept="video/*" onChange={handleFileChange} />
      {loading && (
        <p className="text-slate-500 mt-3">Processing video… this may take a moment.</p>
      )}
      {error && <p className="text-red-600 text-sm mt-3">{error}</p>}

      {result && result.timeline.length > 0 && (
        <>
          <div className="mt-4" style={{ width: "100%", height: 240 }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp_sec"
                  label={{ value: "Time (s)", position: "insideBottom", offset: -5 }}
                />
                <YAxis
                  ticks={emotionOrder.map((_, i) => i)}
                  tickFormatter={(i: number) => emotionOrder[i] ?? ""}
                  width={70}
                />
                <Tooltip
                  formatter={(_value: any, _name: string | number | undefined, props: any) => [
                    `${props.payload.emotion} (${(props.payload.confidence * 100).toFixed(0)}%)`,
                    "Emotion",
                  ]}
                  labelFormatter={(label: any) => `t = ${label}s`}
                />
                <Line type="stepAfter" dataKey="emotionIndex" stroke="#6366f1" dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <ul className="mt-4 space-y-1">
            {result.timeline.map((entry, i) => (
              <li key={i} className="text-slate-700 text-sm">
                {entry.timestamp_sec.toFixed(1)}s — {entry.emotion} —{" "}
                {(entry.confidence * 100).toFixed(0)}% confidence
              </li>
            ))}
          </ul>
        </>
      )}

      {result && result.timeline.length === 0 && (
        <p className="text-slate-500 mt-3">No faces were detected in this video.</p>
      )}
    </div>
  );
}
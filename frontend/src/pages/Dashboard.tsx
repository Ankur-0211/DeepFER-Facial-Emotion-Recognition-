import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { fetchReportsSummary } from "../services/apiClient";

export default function Dashboard() {
  const [data, setData] = useState<{ emotion: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReportsSummary()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold text-slate-800 mb-4">Analytics Dashboard</h1>
      {loading && <p className="text-slate-500">Loading…</p>}
      {!loading && data.length === 0 && (
        <p className="text-slate-500">No predictions logged yet — try the Live Detect page.</p>
      )}
      {data.length > 0 && (
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={data}>
            <XAxis dataKey="emotion" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#1e293b" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
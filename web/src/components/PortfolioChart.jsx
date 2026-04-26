import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function PortfolioChart({ data }) {
  const formatted = data.map(r => ({
    ...r,
    date: r.run_at.slice(0, 10),
    value: parseFloat(r.total_curr_val?.toFixed(2)),
    returnPct: parseFloat((r.total_return * 100)?.toFixed(2)),
  }));

  return (
    <div className="bg-gray-800 rounded-xl p-4">
      <h2 className="text-gray-300 font-semibold mb-4">Portfolio Value Over Time</h2>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={formatted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="date" tick={{ fill: "#9ca3af", fontSize: 11 }} />
          <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} tickFormatter={v => `$${v.toLocaleString()}`} width={80} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1f2937", border: "none", borderRadius: 8 }}
            labelStyle={{ color: "#e5e7eb" }}
            formatter={v => [`$${v.toLocaleString()}`, "Value"]}
          />
          <Line type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

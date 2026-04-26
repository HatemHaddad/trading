import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#0d1424] border border-[#1a2640] rounded-lg px-3 py-2 shadow-2xl">
      <div className="text-slate-500 text-xs mb-1">{label}</div>
      <div className="text-white font-bold text-sm tabular-nums">
        ${payload[0].value?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
    </div>
  );
}

export default function PortfolioChart({ data }) {
  const formatted = data.map(r => ({
    date: r.run_at.slice(0, 10),
    value: parseFloat(r.total_curr_val?.toFixed(2)),
  }));

  const values = formatted.map(d => d.value).filter(Boolean);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const pad = (max - min) * 0.15 || 500;

  return (
    <div className="bg-[#0d1424] border border-[#1a2640] rounded-xl p-5 h-full flex flex-col gap-4">
      <span className="text-slate-500 text-xs font-semibold uppercase tracking-wider">Portfolio Value</span>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={formatted} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="2 4" stroke="#1a2640" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "#334155", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "#334155", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={v => `$${(v / 1000).toFixed(0)}k`}
            width={38}
            domain={[min - pad, max + pad]}
          />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ stroke: "#6366f1", strokeWidth: 1, strokeDasharray: "4 4" }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#grad)"
            dot={false}
            activeDot={{ r: 4, fill: "#6366f1", strokeWidth: 0 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

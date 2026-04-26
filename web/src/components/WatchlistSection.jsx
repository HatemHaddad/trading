import { useEffect, useState } from "react";
import { fetchWatchlist } from "../api";

function pct(n) {
  if (n == null) return "—";
  const v = (n * 100).toFixed(2);
  return `${Number(v) >= 0 ? "+" : ""}${v}%`;
}

function PerfCell({ label, value }) {
  const isPos = value != null && value >= 0;
  return (
    <div className="flex flex-col items-center gap-1 bg-[#080c14] rounded-lg py-2.5 px-1">
      <span className="text-slate-600 text-xs">{label}</span>
      <span className={`font-bold text-sm tabular-nums ${
        value == null ? "text-slate-600" : isPos ? "text-emerald-400" : "text-red-400"
      }`}>
        {pct(value)}
      </span>
    </div>
  );
}

export default function WatchlistSection() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWatchlist().then(setData).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-[#0d1424] border border-[#1a2640] rounded-xl p-5 flex flex-col gap-4">

      {/* Section header */}
      <div className="flex items-center justify-between">
        <span className="text-slate-500 text-xs font-semibold uppercase tracking-wider">Watchlist</span>
        <span className="text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full font-semibold">
          Potential Buy
        </span>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-slate-500 text-sm py-6 justify-center">
          <div className="w-4 h-4 border-2 border-slate-700 border-t-indigo-400 rounded-full animate-spin" />
          Fetching live market data...
        </div>
      )}

      {error && (
        <div className="text-red-400 text-sm py-3 text-center">{error}</div>
      )}

      {data && (
        <div className="flex flex-col gap-4">

          {/* Ticker row */}
          <div className="flex items-start justify-between flex-wrap gap-3">
            <div>
              <div className="text-xl font-bold text-white">{data.ticker}</div>
              <div className="text-slate-500 text-xs mt-0.5">{data.name}</div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold tabular-nums text-white">${data.curr_price?.toFixed(2)}</div>
              <div className={`text-xs font-semibold mt-0.5 ${data.above_ma50 ? "text-emerald-400" : "text-amber-400"}`}>
                {data.above_ma50 ? "▲ Above 50-day MA" : "▼ Below 50-day MA"}
              </div>
            </div>
          </div>

          {/* Performance row */}
          <div className="grid grid-cols-4 gap-2">
            <PerfCell label="1M"  value={data.ret_1m} />
            <PerfCell label="3M"  value={data.ret_3m} />
            <PerfCell label="6M"  value={data.ret_6m} />
            <PerfCell label="1Y"  value={data.ret_1y} />
          </div>

          {/* Risk + Why */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <span className="text-slate-600 text-xs uppercase tracking-wider">Risk Metrics</span>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: "Volatility", value: pct(data.volatility),    color: "text-amber-400" },
                  { label: "Sharpe",     value: data.sharpe?.toFixed(2) ?? "—", color: "text-slate-200" },
                  { label: "Max DD",     value: pct(data.max_drawdown),   color: "text-red-400" },
                ].map(m => (
                  <div key={m.label} className="bg-[#080c14] rounded-lg p-2.5 flex flex-col gap-0.5 text-center">
                    <span className="text-slate-600 text-xs">{m.label}</span>
                    <span className={`font-bold text-sm tabular-nums ${m.color}`}>{m.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <span className="text-slate-600 text-xs uppercase tracking-wider">Why SPMO?</span>
              <ul className="text-xs text-slate-400 space-y-2">
                <li className="flex gap-2">
                  <span className="text-indigo-400 flex-shrink-0 font-bold">→</span>
                  <span>S&P 500 momentum factor — no 3× leverage decay vs TQQQ</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-indigo-400 flex-shrink-0 font-bold">→</span>
                  <span>Broader sector exposure, reduces Nasdaq concentration</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-indigo-400 flex-shrink-0 font-bold">→</span>
                  <span>Middle tier between AGG bonds and leveraged TQQQ</span>
                </li>
              </ul>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}

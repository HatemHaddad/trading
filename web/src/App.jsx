import { useEffect, useState } from "react";
import { fetchLatest, fetchHistory, fetchRuns } from "./api";
import StatCard from "./components/StatCard";
import PortfolioChart from "./components/PortfolioChart";
import QuarterlyTarget from "./components/QuarterlyTarget";
import RunsTable from "./components/RunsTable";

function fmt(n, digits = 2) {
  return n != null ? `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits })}` : "—";
}
function pct(n) {
  if (n == null) return "—";
  const v = (n * 100).toFixed(2);
  return `${v >= 0 ? "+" : ""}${v}%`;
}

export default function App() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([fetchLatest(), fetchHistory(), fetchRuns()])
      .then(([l, h, r]) => {
        setLatest(l);
        setHistory(h);
        setRuns(r.runs);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center text-gray-400 text-lg">
      Loading portfolio data...
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center text-red-400 text-lg">
      Error: {error} — is the API running?
    </div>
  );

  const retColor = latest.total_return >= 0 ? "text-green-400" : "text-red-400";
  const tqqqColor = latest.return_tqqq >= 0 ? "text-green-400" : "text-red-400";
  const aggColor = latest.return_agg >= 0 ? "text-green-400" : "text-red-400";

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto flex flex-col gap-6">

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-indigo-400">Trading Portfolio</h1>
          <span className="text-gray-500 text-sm">Last run: {latest.run_at}</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Total Value" value={fmt(latest.total_curr_val)} sub={`Invested: ${fmt(latest.total_buy_val)}`} />
          <StatCard label="Total Return" value={pct(latest.total_return)} sub={`P&L: ${fmt(latest.total_profit)}`} color={retColor} />
          <StatCard label="Sharpe Ratio" value={latest.sharpe?.toFixed(2) ?? "—"} sub="Annualised" />
          <StatCard label="Max Drawdown" value={pct(latest.max_drawdown)} sub="1-year window" color="text-red-400" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-800 rounded-xl p-4 flex flex-col gap-2">
            <h2 className="text-gray-300 font-semibold">TQQQ</h2>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div><span className="text-gray-500 block">Price</span><span className="font-bold">${latest.price_tqqq?.toFixed(2)}</span></div>
              <div><span className="text-gray-500 block">Shares</span><span className="font-bold">{latest.shares_tqqq?.toFixed(4)}</span></div>
              <div><span className="text-gray-500 block">Value</span><span className="font-bold">{fmt(latest.curr_val_tqqq)}</span></div>
              <div><span className="text-gray-500 block">Buy Price</span><span className="font-bold">${latest.buy_price_tqqq?.toFixed(2)}</span></div>
              <div><span className="text-gray-500 block">P&L</span><span className={`font-bold ${tqqqColor}`}>{fmt(latest.profit_tqqq)}</span></div>
              <div><span className="text-gray-500 block">Return</span><span className={`font-bold ${tqqqColor}`}>{pct(latest.return_tqqq)}</span></div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-xl p-4 flex flex-col gap-2">
            <h2 className="text-gray-300 font-semibold">AGG</h2>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div><span className="text-gray-500 block">Price</span><span className="font-bold">${latest.price_agg?.toFixed(2)}</span></div>
              <div><span className="text-gray-500 block">Shares</span><span className="font-bold">{latest.shares_agg?.toFixed(4)}</span></div>
              <div><span className="text-gray-500 block">Value</span><span className="font-bold">{fmt(latest.curr_val_agg)}</span></div>
              <div><span className="text-gray-500 block">Buy Price</span><span className="font-bold">${latest.buy_price_agg?.toFixed(2)}</span></div>
              <div><span className="text-gray-500 block">P&L</span><span className={`font-bold ${aggColor}`}>{fmt(latest.profit_agg)}</span></div>
              <div><span className="text-gray-500 block">Return</span><span className={`font-bold ${aggColor}`}>{pct(latest.return_agg)}</span></div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <PortfolioChart data={history} />
          </div>
          <QuarterlyTarget data={latest} />
        </div>

        <RunsTable runs={runs} />

      </div>
    </div>
  );
}

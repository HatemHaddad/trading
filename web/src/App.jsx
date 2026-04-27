import { useEffect, useState } from "react";
import { fetchLatest, fetchHistory, fetchRuns } from "./api";
import PortfolioChart from "./components/PortfolioChart";
import QuarterlyTarget from "./components/QuarterlyTarget";
import RunsTable from "./components/RunsTable";
import WatchlistSection from "./components/WatchlistSection";

function fmt(n, d = 2) {
  return n != null
    ? `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d })}`
    : "—";
}
function fmtAED(n, d = 2) {
  return n != null
    ? `AED ${Number(n).toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d })}`
    : "—";
}
function pct(n) {
  if (n == null) return "—";
  const v = (n * 100).toFixed(2);
  return `${Number(v) >= 0 ? "+" : ""}${v}%`;
}
function retColor(n) {
  return n == null ? "text-slate-400" : n >= 0 ? "text-emerald-400" : "text-red-400";
}

function MetricPill({ label, value, color = "text-slate-200" }) {
  return (
    <div className="bg-[#0d1424] border border-[#1a2640] rounded-xl px-4 py-3 flex flex-col gap-1">
      <span className="text-slate-500 text-xs uppercase tracking-wider">{label}</span>
      <span className={`text-lg font-bold tabular-nums ${color}`}>{value}</span>
    </div>
  );
}

function HoldingCard({ ticker, price, shares, buyPrice, currVal, profit, ret, alloc, color, isAED = false, usdEquiv, aedRate }) {
  const allocPct = alloc != null ? Math.round(alloc * 100) : 0;
  const priceStr = isAED
    ? (price != null ? `AED ${price.toFixed(3)}` : "—")
    : `$${price?.toFixed(2) ?? "—"}`;
  const costStr  = isAED ? `AED ${buyPrice?.toFixed(3)}` : `$${buyPrice?.toFixed(2)}`;
  const valStr   = isAED ? fmtAED(currVal) : fmt(currVal);
  const plStr    = isAED ? fmtAED(profit)  : fmt(profit);

  return (
    <div className="bg-[#0d1424] border border-[#1a2640] rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-slate-500 text-xs uppercase tracking-widest">Holding</span>
            {isAED && (
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase tracking-wider">AED</span>
            )}
          </div>
          <div className="text-2xl font-bold text-white mt-1">{ticker}</div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold tabular-nums text-slate-200">{priceStr}</div>
          <div className={`text-sm font-semibold tabular-nums mt-0.5 ${color}`}>{pct(ret)}</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Shares",   value: shares?.toLocaleString(undefined, { maximumFractionDigits: 0 }) },
          { label: "Avg Cost", value: costStr },
          { label: "Value",    value: valStr },
        ].map(({ label, value }) => (
          <div key={label} className="flex flex-col gap-0.5">
            <span className="text-slate-600 text-xs">{label}</span>
            <span className="text-slate-200 font-semibold text-sm tabular-nums">{value}</span>
          </div>
        ))}
      </div>

      <div className="bg-[#080c14] rounded-lg px-3 py-2.5 flex items-center justify-between">
        <span className="text-slate-500 text-xs">Unrealised P&L</span>
        <span className={`font-bold tabular-nums text-sm ${color}`}>{plStr}</span>
      </div>

      {isAED && usdEquiv != null && (
        <div className="bg-[#080c14] rounded-lg px-3 py-2.5 flex items-center justify-between">
          <span className="text-slate-500 text-xs">≈ USD Value</span>
          <div className="text-right">
            <span className="text-slate-300 font-semibold tabular-nums text-sm">{fmt(usdEquiv)}</span>
            {aedRate != null && (
              <div className="text-slate-600 text-[10px] tabular-nums">1 USD = {aedRate.toFixed(4)} AED</div>
            )}
          </div>
        </div>
      )}

      <div>
        <div className="flex justify-between text-xs mb-1.5">
          <span className="text-slate-600">Allocation</span>
          <span className="text-slate-400 font-semibold">{allocPct}%</span>
        </div>
        <div className="h-1.5 bg-[#1a2640] rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full"
            style={{ width: `${allocPct}%` }}
          />
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([fetchLatest(), fetchHistory(), fetchRuns()])
      .then(([l, h, r]) => { setLatest(l); setHistory(h); setRuns(r.runs); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="min-h-screen bg-[#080c14] flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-slate-500 text-sm">Loading portfolio...</span>
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-[#080c14] flex items-center justify-center px-4">
      <div className="text-center">
        <div className="text-red-400 text-lg font-semibold mb-2">Connection Error</div>
        <div className="text-slate-500 text-sm">{error}</div>
        <div className="text-slate-600 text-xs mt-1">Is the API running on port 8000?</div>
      </div>
    </div>
  );

  const totalRet = latest.total_return;
  const retC = retColor(totalRet);

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-200">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-5">

        {/* ── Header ── */}
        <div className="flex items-start justify-between flex-wrap gap-4 pb-2">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 inline-block" />
              <span className="text-indigo-400 text-xs font-semibold uppercase tracking-widest">Portfolio Dashboard</span>
            </div>
            <div className="text-4xl sm:text-5xl font-bold text-white tabular-nums leading-none">
              {fmt(latest.total_curr_val)}
            </div>
            <div className="flex items-center gap-3 mt-2.5 text-sm flex-wrap">
              <span className={`font-bold tabular-nums ${retC}`}>{pct(totalRet)}</span>
              <span className="text-slate-700">·</span>
              <span className="text-slate-500">P&L <span className={`font-semibold tabular-nums ${retC}`}>{fmt(latest.total_profit)}</span></span>
              <span className="text-slate-700">·</span>
              <span className="text-slate-500">Cost <span className="text-slate-300 font-semibold tabular-nums">{fmt(latest.total_buy_val)}</span></span>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-slate-500 text-xs mt-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-mono text-slate-400">{latest.run_at}</span>
          </div>
        </div>

        {/* ── Metrics strip ── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <MetricPill label="Sharpe Ratio" value={latest.sharpe?.toFixed(2) ?? "—"} />
          <MetricPill label="Max Drawdown" value={pct(latest.max_drawdown)} color="text-red-400" />
          <MetricPill label="Ann. Return"  value={latest.ann_return != null ? pct(latest.ann_return) : "—"} color={retColor(latest.ann_return)} />
          <MetricPill label="Volatility"   value={latest.volatility != null ? pct(latest.volatility) : "—"} color="text-amber-400" />
        </div>

        {/* ── Holdings ── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <HoldingCard ticker="TQQQ" price={latest.price_tqqq} shares={latest.shares_tqqq}
            buyPrice={latest.buy_price_tqqq} currVal={latest.curr_val_tqqq}
            profit={latest.profit_tqqq} ret={latest.return_tqqq} alloc={latest.alloc_tqqq}
            color={retColor(latest.return_tqqq)} />
          <HoldingCard ticker="AGG" price={latest.price_agg} shares={latest.shares_agg}
            buyPrice={latest.buy_price_agg} currVal={latest.curr_val_agg}
            profit={latest.profit_agg} ret={latest.return_agg} alloc={latest.alloc_agg}
            color={retColor(latest.return_agg)} />
          <HoldingCard ticker="IBIT" price={latest.price_ibit} shares={latest.shares_ibit}
            buyPrice={latest.buy_price_ibit} currVal={latest.curr_val_ibit}
            profit={latest.profit_ibit} ret={latest.return_ibit} alloc={latest.alloc_ibit}
            color={retColor(latest.return_ibit)} />
          <HoldingCard ticker="ADC" price={latest.price_adc} shares={latest.shares_adc}
            buyPrice={latest.buy_price_adc} currVal={latest.curr_val_adc}
            profit={latest.profit_adc} ret={latest.return_adc} alloc={latest.alloc_adc}
            color={retColor(latest.return_adc)}
            isAED={true} usdEquiv={latest.curr_val_adc_usd} aedRate={latest.aed_usd_rate} />
        </div>

        {/* ── Chart + Quarterly ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <PortfolioChart data={history} />
          </div>
          <QuarterlyTarget data={latest} />
        </div>

        {/* ── SPMO Watchlist ── */}
        <WatchlistSection />

        {/* ── History ── */}
        <RunsTable runs={runs} />

      </div>
    </div>
  );
}

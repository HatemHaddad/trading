export default function QuarterlyTarget({ data }) {
  const perfPct = data.quarter_perf * 100;
  const progress = Math.min(Math.max(perfPct / 9, 0), 1);

  const r = 38;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - progress);

  const isPos = perfPct >= 0;
  const action = data.quarter_action;
  const actionStyle =
    action === "BUY"  ? { text: "text-emerald-400", bg: "bg-emerald-400/10 border-emerald-400/20" } :
    action === "SELL" ? { text: "text-red-400",     bg: "bg-red-400/10 border-red-400/20" } :
                        { text: "text-amber-400",   bg: "bg-amber-400/10 border-amber-400/20" };

  return (
    <div className="bg-[#0d1424] border border-[#1a2640] rounded-xl p-5 flex flex-col gap-5">
      <span className="text-slate-500 text-xs font-semibold uppercase tracking-wider">Quarterly Target</span>

      {/* Circle progress */}
      <div className="flex items-center justify-center">
        <div className="relative w-[96px] h-[96px]">
          <svg width={96} height={96} className="-rotate-90 absolute inset-0">
            <circle cx={48} cy={48} r={r} fill="none" stroke="#1a2640" strokeWidth={7} />
            <circle
              cx={48} cy={48} r={r}
              fill="none"
              stroke={isPos ? "#6366f1" : "#ef4444"}
              strokeWidth={7}
              strokeLinecap="round"
              strokeDasharray={circ}
              strokeDashoffset={offset}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`font-bold text-lg tabular-nums leading-none ${isPos ? "text-emerald-400" : "text-red-400"}`}>
              {perfPct.toFixed(1)}%
            </span>
            <span className="text-slate-600 text-xs mt-0.5">of 9%</span>
          </div>
        </div>
      </div>

      {/* Action badge */}
      <div className="flex justify-center">
        <span className={`text-xs font-bold px-3 py-1 rounded-full border ${actionStyle.text} ${actionStyle.bg}`}>
          {action}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-2">
        {[
          { label: "Shares to trade", value: data.shares_to_trade?.toFixed(2) ?? "—" },
          { label: "Gap to target",   value: `$${Math.abs(data.quarter_gap)?.toFixed(0) ?? "—"}` },
          { label: "Target value",    value: `$${data.quarter_target_value?.toLocaleString(undefined, {maximumFractionDigits: 0}) ?? "—"}` },
          { label: "Current value",   value: `$${data.quarter_start_value?.toLocaleString(undefined, {maximumFractionDigits: 0}) ?? "—"}` },
        ].map(({ label, value }) => (
          <div key={label} className="bg-[#080c14] rounded-lg p-2.5 flex flex-col gap-0.5">
            <span className="text-slate-600 text-xs">{label}</span>
            <span className="text-slate-200 font-semibold text-sm tabular-nums">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

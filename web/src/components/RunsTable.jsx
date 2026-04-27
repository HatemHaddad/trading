export default function RunsTable({ runs }) {
  return (
    <div className="bg-[#0d1424] border border-[#1a2640] rounded-xl p-5">
      <span className="text-slate-500 text-xs font-semibold uppercase tracking-wider">Run History</span>
      <div className="overflow-x-auto mt-4">
        <table className="w-full text-sm text-left min-w-[420px]">
          <thead>
            <tr className="text-slate-600 text-xs uppercase tracking-wider border-b border-[#1a2640]">
              <th className="pb-3 pr-4 font-medium">Date</th>
              <th className="pb-3 pr-4 font-medium">Value</th>
              <th className="pb-3 pr-4 font-medium">Return</th>
              <th className="pb-3 pr-4 font-medium hidden sm:table-cell">TQQQ</th>
              <th className="pb-3 pr-4 font-medium hidden sm:table-cell">AGG</th>
              <th className="pb-3 pr-4 font-medium hidden sm:table-cell">IBIT</th>
              <th className="pb-3 pr-4 font-medium hidden lg:table-cell">ADC (AED)</th>
              <th className="pb-3 pr-4 font-medium hidden sm:table-cell">Day Chg</th>
              <th className="pb-3 pr-4 font-medium hidden md:table-cell">Sharpe</th>
              <th className="pb-3 font-medium">Signal</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1a2640]">
            {runs.map((r, i) => {
              const ret = (r.total_return * 100).toFixed(2);
              const retC = r.total_return >= 0 ? "text-emerald-400" : "text-red-400";
              const aStyle =
                r.quarter_action === "BUY"  ? "text-emerald-400 bg-emerald-400/10 border-emerald-400/20" :
                r.quarter_action === "SELL" ? "text-red-400 bg-red-400/10 border-red-400/20" :
                                              "text-amber-400 bg-amber-400/10 border-amber-400/20";
              return (
                <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-2.5 pr-4 font-mono text-xs text-slate-500 whitespace-nowrap">{r.run_at.slice(0, 10)}</td>
                  <td className="py-2.5 pr-4 text-slate-200 font-semibold tabular-nums whitespace-nowrap">
                    ${r.total_curr_val?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className={`py-2.5 pr-4 font-semibold tabular-nums whitespace-nowrap ${retC}`}>
                    {ret >= 0 ? "+" : ""}{ret}%
                  </td>
                  <td className="py-2.5 pr-4 text-slate-400 tabular-nums hidden sm:table-cell">${r.price_tqqq?.toFixed(2)}</td>
                  <td className="py-2.5 pr-4 text-slate-400 tabular-nums hidden sm:table-cell">${r.price_agg?.toFixed(2)}</td>
                  <td className="py-2.5 pr-4 text-slate-400 tabular-nums hidden sm:table-cell">{r.price_ibit != null ? `$${r.price_ibit.toFixed(2)}` : "—"}</td>
                  <td className="py-2.5 pr-4 text-slate-400 tabular-nums hidden lg:table-cell">{r.price_adc != null ? `${r.price_adc.toFixed(3)}` : "—"}</td>
                  <td className={`py-2.5 pr-4 font-semibold tabular-nums hidden sm:table-cell whitespace-nowrap ${r.daily_change_pct == null ? "text-slate-600" : r.daily_change_pct >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {r.daily_change_pct != null
                      ? `${r.daily_change_pct >= 0 ? "+" : ""}${(r.daily_change_pct * 100).toFixed(2)}%`
                      : "—"}
                  </td>
                  <td className="py-2.5 pr-4 text-slate-400 tabular-nums hidden md:table-cell">{r.sharpe?.toFixed(2) ?? "—"}</td>
                  <td className="py-2.5">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${aStyle}`}>
                      {r.quarter_action}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function RunsTable({ runs }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 overflow-x-auto">
      <h2 className="text-gray-300 font-semibold mb-4">Run History</h2>
      <table className="w-full text-sm text-left text-gray-400">
        <thead className="text-xs text-gray-500 uppercase border-b border-gray-700">
          <tr>
            <th className="pb-2 pr-4">Date</th>
            <th className="pb-2 pr-4">Total Value</th>
            <th className="pb-2 pr-4">Return</th>
            <th className="pb-2 pr-4">TQQQ</th>
            <th className="pb-2 pr-4">AGG</th>
            <th className="pb-2 pr-4">Sharpe</th>
            <th className="pb-2">Action</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((r, i) => {
            const ret = (r.total_return * 100).toFixed(2);
            const retColor = r.total_return >= 0 ? "text-green-400" : "text-red-400";
            const actionColor = r.quarter_action === "BUY"
              ? "text-green-400" : r.quarter_action === "SELL"
              ? "text-red-400" : "text-yellow-400";
            return (
              <tr key={i} className="border-b border-gray-700 hover:bg-gray-750">
                <td className="py-2 pr-4 whitespace-nowrap">{r.run_at.slice(0, 16)}</td>
                <td className="py-2 pr-4">${r.total_curr_val?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td className={`py-2 pr-4 ${retColor}`}>{ret >= 0 ? "+" : ""}{ret}%</td>
                <td className="py-2 pr-4">${r.price_tqqq?.toFixed(2)}</td>
                <td className="py-2 pr-4">${r.price_agg?.toFixed(2)}</td>
                <td className="py-2 pr-4">{r.sharpe?.toFixed(2) ?? "—"}</td>
                <td className={`py-2 font-semibold ${actionColor}`}>{r.quarter_action}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

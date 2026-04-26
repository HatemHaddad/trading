export default function QuarterlyTarget({ data }) {
  const pct = data.quarter_perf * 100;
  const progress = Math.min(Math.max((pct / 9) * 100, 0), 100);
  const actionColor = data.quarter_action === "BUY"
    ? "text-green-400" : data.quarter_action === "SELL"
    ? "text-red-400" : "text-yellow-400";

  return (
    <div className="bg-gray-800 rounded-xl p-4 flex flex-col gap-3">
      <h2 className="text-gray-300 font-semibold">Quarterly Target (9%)</h2>
      <div className="flex justify-between text-sm text-gray-400">
        <span>Progress</span>
        <span className={pct >= 0 ? "text-green-400" : "text-red-400"}>{pct.toFixed(2)}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-3">
        <div
          className="bg-indigo-500 h-3 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="grid grid-cols-3 gap-2 mt-1 text-sm">
        <div className="flex flex-col">
          <span className="text-gray-500">Action</span>
          <span className={`font-bold ${actionColor}`}>{data.quarter_action}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-gray-500">Shares</span>
          <span className="text-white font-semibold">{data.shares_to_trade?.toFixed(2) ?? "—"}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-gray-500">Gap</span>
          <span className="text-white font-semibold">${data.quarter_gap?.toFixed(2) ?? "—"}</span>
        </div>
      </div>
    </div>
  );
}

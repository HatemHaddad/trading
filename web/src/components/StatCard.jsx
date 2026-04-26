export default function StatCard({ label, value, sub, color = "text-white" }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 flex flex-col gap-1">
      <span className="text-gray-400 text-sm">{label}</span>
      <span className={`text-2xl font-bold ${color}`}>{value}</span>
      {sub && <span className="text-gray-500 text-xs">{sub}</span>}
    </div>
  );
}

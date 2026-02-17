export default function StatCard({
  title,
  value,
  percentage,
  isPositive = true,
  icon,
}) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-center justify-between">
      
      {/* Left Side */}
      <div>
        <p className="text-sm text-gray-400">{title}</p>

        <div className="flex items-center gap-2 mt-1">
          <h2 className="text-xl font-bold text-gray-800">{value}</h2>

          <span
            className={`text-sm font-medium ${
              isPositive ? "text-green-500" : "text-red-500"
            }`}
          >
            {percentage}
          </span>
        </div>
      </div>

      {/* Right Side Icon */}
      <div className="w-10 h-10 rounded-lg bg-teal-400 flex items-center justify-center text-white">
        {icon}
      </div>
    </div>
  );
}

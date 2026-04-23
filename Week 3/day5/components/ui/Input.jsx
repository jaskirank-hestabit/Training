export default function Input({
  label,
  type = "text",
  className = "",
  ...props
}) {
  return (
    <div className="flex flex-col gap-1 w-full">
      {label && (
        <label className="text-sm text-gray-600">{label}</label>
      )}
      <input
        type={type}
        className={`px-4 py-2 border rounded-lg bg-gray-50 focus:ring-2 focus:ring-teal-400 focus:outline-none ${className}`}
        {...props}
      />
    </div>
  );
}

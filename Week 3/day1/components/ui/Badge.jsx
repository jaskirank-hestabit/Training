export default function Badge({ children, variant = "success" }) {
  const variants = {
    success: "bg-green-100 text-green-600",
    warning: "bg-yellow-100 text-yellow-700",
    error: "bg-red-100 text-red-600",
    info: "bg-blue-100 text-blue-600",
  };

  return (
    <span
      className={`px-3 py-1 text-xs font-medium rounded-full ${variants[variant]}`}
    >
      {children}
    </span>
  );
}

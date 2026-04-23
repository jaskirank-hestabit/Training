export default function Card({ children, className = "" }) {
  const hasCustomBg = className.includes("bg-");

  return (
    <div
      className={`
        ${!hasCustomBg ? "bg-white" : ""}
        rounded-xl shadow-sm border border-gray-100 p-6
        ${className}
      `}
    >
      {children}
    </div>
  );
}

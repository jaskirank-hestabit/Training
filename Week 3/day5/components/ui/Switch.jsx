export default function Switch({ checked = false }) {
  return (
    <div
      className={`relative w-11 h-6 rounded-full transition ${
        checked ? "bg-teal-500" : "bg-gray-300"
      }`}
    >
      <span
        className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition ${
          checked ? "translate-x-5" : ""
        }`}
      />
    </div>
  );
}

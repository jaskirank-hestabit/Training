import Link from "next/link";

export default function LandingNavbar() {
  return (
    <header className="fixed top-0 left-0 w-full z-50 bg-black border-b border-gray-800">
      <div className="max-w-10xl mx-auto px-6 h-16 flex items-center justify-between">

        {/* LEFT - Logo */}
        <Link
          href="/"
          className="text-xl font-bold text-teal-400 hover:opacity-80 transition"
        >
          Velora
        </Link>

        {/* RIGHT - Pricing + Sign Up */}
        <div className="flex items-center gap-6 text-sm">
            <Link
            href="/about"
            className="text-gray-300 hover:text-white transition"
          >
            About
          </Link>

          <Link
            href="/pricing"
            className="text-gray-300 hover:text-white transition"
          >
            Pricing
          </Link>

          <Link href="/signup">
            <button className="px-4 py-1.5 rounded-full bg-teal-500 text-white hover:bg-teal-600 transition">
              Sign Up
            </button>
          </Link>

        </div>

      </div>
    </header>
  );
}

import Link from "next/link";

export default function LandingFooter() {
  return (
    <footer className="bg-gray-900 text-gray-300 py-10">
      <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-sm">
          © {new Date().getFullYear()} ProjectFlow. All rights reserved.
        </p>

        <div className="flex gap-6 text-sm">
          <Link href="#">Privacy</Link>
          <Link href="#">Terms</Link>
          <Link href="#">Contact</Link>
        </div>
      </div>
    </footer>
  );
}

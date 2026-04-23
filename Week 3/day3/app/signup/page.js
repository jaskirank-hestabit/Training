import Image from "next/image";
import Link from "next/link";
import Button from "@/components/ui/Button"; // adjust path if needed

export default function SignupPage() {
  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-gray-50">
      {/* LEFT SIDE */}
      <div className="relative flex items-center justify-center px-6 py-12">
        {/* Logo */}
        <Link
          href="/"
          className="absolute top-8 left-8 text-2xl font-extrabold text-teal-500 hover:opacity-80 transition"
        >
          Velora
        </Link>

        {/* Center Card */}
        <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 space-y-6">
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold">Create Your Account</h1>
            <p className="text-gray-500 text-sm">
              Start managing your projects and growing revenue today.
            </p>
          </div>

          <form className="space-y-5">
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">
                Full Name
              </label>
              <input
                type="text"
                placeholder="John Doe"
                className="w-full px-4 py-3 rounded-lg border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-400 transition"
              />
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">
                Email Address
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full px-4 py-3 rounded-lg border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-400 transition"
              />
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                type="password"
                placeholder="••••••••"
                className="w-full px-4 py-3 rounded-lg border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-400 transition"
              />
            </div>
            
            <Link href="/dashboard">
                <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full shadow-md hover:shadow-lg"
                >
                Sign Up
                </Button>
            </Link>
          </form>

          <p className="text-sm text-gray-500 text-center pt-2">
            Existing user?{" "}
            <Link
              href="/login"
              className="text-teal-500 font-medium hover:underline"
            >
              Login
            </Link>
          </p>
        </div>
      </div>

      {/* RIGHT SIDE IMAGE */}
      <div className="relative hidden lg:flex justify-end">
        <div className="relative w-full h-[92%] rounded-bl-[60px] overflow-hidden shadow-2xl">
          <Image
            src="/images/signup-image.jpg"
            alt="Signup Visual"
            fill
            priority
            className="object-cover"
          />
        </div>
      </div>
    </div>
  );
}

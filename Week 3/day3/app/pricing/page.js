import Link from "next/link";
import LandingNavbar from "@/components/landing/LandingNavbar";

export const metadata = {
  title: "Pricing - ProjectFlow",
  description: "Choose the perfect plan for your business growth.",
};

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <LandingNavbar />

      <section className="pt-32 pb-20 px-6">
        <div className="max-w-6xl mx-auto text-center space-y-6">
          <h1 className="text-4xl md:text-5xl font-bold">
            Simple, Transparent Pricing
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Choose the plan that fits your workflow and start managing projects
            smarter.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="mt-16 grid gap-8 md:grid-cols-3 max-w-6xl mx-auto">
          {/* FREE PLAN */}
          <div
            className="bg-white border rounded-2xl p-8 shadow-sm 
            flex flex-col transition-all duration-300 ease-out 
            hover:-translate-y-2 hover:shadow-xl"
          >
            <h3 className="text-xl font-semibold">Free</h3>
            <p className="mt-4 text-5xl font-extrabold">$0</p>
            <p className="text-gray-500 mb-6">Forever free</p>

            <ul className="space-y-3 text-sm flex-1 text-gray-700">
              <li>✔ 3 Active Projects</li>
              <li>✔ Basic Revenue Tracking</li>
              <li>✔ Client Management</li>
              <li>✔ Email Support</li>
            </ul>

            <Link
              href="/signup"
              className="mt-8 block text-center bg-teal-600 text-white py-3 rounded-lg font-medium hover:bg-teal-700 transition"
            >
              Get Started
            </Link>
          </div>

          {/* PRO PLAN (Highlighted) */}
          <div
            className="bg-teal-600 text-white rounded-2xl p-8 
            shadow-lg scale-105 flex flex-col 
            transition-all duration-300 ease-out 
            hover:-translate-y-2 hover:scale-110 hover:shadow-2xl"
          >
            <span className="text-sm bg-white text-teal-700 px-3 py-1 rounded-full self-start mb-4 font-semibold">
              Most Popular
            </span>

            <h3 className="text-xl font-semibold">Pro</h3>
            <p className="mt-4 text-5xl font-extrabold">$29</p>
            <p className="text-teal-100 mb-6">per month</p>

            <ul className="space-y-3 text-sm flex-1 text-teal-50">
              <li>✔ Unlimited Projects</li>
              <li>✔ Advanced Revenue Analytics</li>
              <li>✔ Priority Client Management</li>
              <li>✔ Team Collaboration</li>
              <li>✔ Priority Support</li>
            </ul>

            <Link
              href="/signup"
              className="mt-8 block text-center bg-white text-teal-700 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
            >
              Upgrade to Pro
            </Link>
          </div>

          {/* PREMIUM PLAN */}
          <div
            className="bg-white border rounded-2xl p-8 shadow-sm 
            flex flex-col transition-all duration-300 ease-out 
            hover:-translate-y-2 hover:shadow-xl"
          >
            <h3 className="text-xl font-semibold">Premium</h3>
            <p className="mt-4 text-5xl font-extrabold">$59</p>
            <p className="text-gray-500 mb-6">per month</p>

            <ul className="space-y-3 text-sm flex-1 text-gray-700">
              <li>✔ Everything in Pro</li>
              <li>✔ Dedicated Account Manager</li>
              <li>✔ Custom Reports</li>
              <li>✔ Advanced Security Controls</li>
              <li>✔ 24/7 Premium Support</li>
            </ul>

            <Link
              href="/signup"
              className="mt-8 block text-center bg-teal-600 text-white py-3 rounded-lg font-medium hover:bg-teal-700 transition"
            >
              Go Premium
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

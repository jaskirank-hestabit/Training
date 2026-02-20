import Image from "next/image";
import Link from "next/link";
import Button from "@/components/ui/Button";

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 pt-24">
      <div className="max-w-4xl space-y-8">
        <h1 className="text-4xl sm:text-6xl font-extrabold leading-tight tracking-tight">
          Manage Projects.
          <br />
          <span className="text-teal-600">Track Revenue.</span>
          <br />
          Grow Your Business.
        </h1>

        <p className="text-gray-300 text-xl max-w-2xl mx-auto">
          A powerful SaaS dashboard built to simplify workflows and accelerate growth.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/signup">
            <Button size="lg">Get Started</Button>
          </Link>
          <Link href="/dashboard">
            <Button variant="secondary" size="lg">
              View Dashboard
            </Button>
          </Link>
        </div>
      </div>

      <div className="relative w-full max-w-5xl h-[450px] mt-20 rounded-2xl overflow-hidden shadow-2xl">
        <Image
          src="/images/dashboard-preview.jpg"
          alt="Dashboard preview showing project tracking and revenue dashboard"
          fill
          priority
          sizes="(max-width: 768px) 100vw, 1200px"
          className="object-cover"
        />
      </div>
    </section>
  );
}

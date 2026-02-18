import Link from "next/link";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col justify-center">

      <div className="space-y-24 py-16">

        {/* Hero Section */}
        <section className="max-w-5xl mx-auto text-center px-6 space-y-6">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight">
            Manage Projects. Track Revenue. Grow Your Business.
          </h1>

          <p className="text-gray-600 text-base sm:text-lg max-w-2xl mx-auto">
            A simple and powerful platform to monitor your projects,
            clients, and earnings — all in one organized dashboard.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
            <Button size="lg">Get Started</Button>

            <Link href="/dashboard">
              <Button variant="secondary" size="lg">
                View Dashboard
              </Button>
            </Link>
          </div>
        </section>

        {/* Features Section */}
        <section className="max-w-6xl mx-auto px-6 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          
          <Card className="text-center space-y-4">
            <h3 className="text-xl font-semibold">
              Project Tracking
            </h3>
            <p className="text-gray-600 text-sm">
              Keep track of ongoing and completed projects with
              clear status updates and organized workflows.
            </p>
          </Card>

          <Card className="text-center space-y-4">
            <h3 className="text-xl font-semibold">
              Revenue Insights
            </h3>
            <p className="text-gray-600 text-sm">
              Monitor your earnings, view performance metrics,
              and understand business growth at a glance.
            </p>
          </Card>

          <Card className="text-center space-y-4">
            <h3 className="text-xl font-semibold">
              Client Management
            </h3>
            <p className="text-gray-600 text-sm">
              Maintain client records, manage communication,
              and build long-term professional relationships.
            </p>
          </Card>

        </section>

      </div>
    </div>
  );
}

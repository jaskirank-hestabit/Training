import LandingNavbar from "@/components/landing/LandingNavbar";
import Card from "@/components/ui/Card";

export default function AboutPage() {
  return (
    <div className="max-w-6xl mx-auto mt-14 px-6 py-16 space-y-15">
      <LandingNavbar />
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-teal-500">
          Building Smarter Business Infrastructure
        </h1>
        <p className="text-gray-600 max-w-3xl mx-auto text-lg">
          We help modern teams manage users, monitor analytics, and track
          revenue — all inside one powerful and beautifully designed platform.
        </p>
      </div>

      {/* Trust Section */}
      <div className="text-center space-y-6">
        <p className="text-sm uppercase tracking-wider text-gray-400">
          Trusted by fast-growing companies
        </p>

        <div className="flex flex-wrap justify-center gap-8 text-teal-500 font-semibold">
          <span>Stripe</span>
          <span>Notion</span>
          <span>Vercel</span>
          <span>Shopify</span>
          <span>Slack</span>
        </div>
      </div>

      {/* Mission Section */}
      <Card>
        <SectionTitle title="Our Mission" />
        <p className="text-gray-600 leading-relaxed max-w-3xl">
          Our mission is to simplify business management by combining analytics,
          performance tracking, and user insights into a single intuitive
          dashboard. We believe teams should spend less time switching tools and
          more time building impactful products.
        </p>
      </Card>

      {/* What We Offer */}
      <div className="grid md:grid-cols-3 gap-6">
        <FeatureCard
          title="Real-Time Analytics"
          description="Make data-driven decisions with live dashboards and performance insights."
        />
        <FeatureCard
          title="Revenue Tracking"
          description="Monitor revenue streams, growth metrics, and financial health in one place."
        />
        <FeatureCard
          title="Team Management"
          description="Manage users, roles, and permissions with full visibility and control."
        />
      </div>

      {/* Stats Section */}
      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
        <Card className="bg-teal-500 text-white border-none">
          <h3 className="text-3xl font-bold">10K+</h3>
          <p className="text-sm mt-2 opacity-90">Active Users</p>
        </Card>

        <Card className="bg-teal-500 text-white border-none">
          <h3 className="text-3xl font-bold">250+</h3>
          <p className="text-sm mt-2 opacity-90">Companies</p>
        </Card>

        <Card className="bg-teal-500 text-white border-none">
          <h3 className="text-3xl font-bold">99.9%</h3>
          <p className="text-sm mt-2 opacity-90">Uptime</p>
        </Card>
      </div>

      {/* Core Values */}
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Our Core Values</h2>
          <p className="text-gray-600 mt-2">
            The principles that guide everything we build.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <ValueCard
            title="Simplicity"
            description="We design clean, intuitive experiences that remove friction."
          />
          <ValueCard
            title="Performance"
            description="Optimized architecture ensures fast, reliable performance."
          />
          <ValueCard
            title="Scalability"
            description="Built to grow with your business, from startup to enterprise."
          />
        </div>
      </div>
    </div>
  );
}

/* Reusable Section Title */
function SectionTitle({ title }) {
  return <h2 className="text-xl font-semibold mb-4">{title}</h2>;
}

/* Feature Card */
function FeatureCard({ title, description }) {
  return (
    <Card>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </Card>
  );
}

/* Value Card */
function ValueCard({ title, description }) {
  return (
    <Card>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </Card>
  );
}

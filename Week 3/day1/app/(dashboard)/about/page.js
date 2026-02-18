import Card from "@/components/ui/Card";

export default function AboutPage() {
  return (
    <div className="max-w-5xl mx-auto space-y-10 pt-10">
      {/* Page Heading */}
      <div className="space-y-3">
        <h1 className="text-3xl font-bold">About Our Platform</h1>
        <p className="text-gray-600 max-w-2xl">
          Our application is designed to help businesses manage users,
          monitor analytics, track revenue, and streamline operations all in
          one place.
        </p>
      </div>

      {/* Mission Section */}
      <Card>
        <SectionTitle title="Our Mission" />
        <p className="text-gray-600 leading-relaxed">
          We aim to simplify business management by providing intuitive tools
          that combine analytics, performance tracking, and user insights into a
          single, elegant interface. Our goal is to empower teams to make
          data-driven decisions faster and more efficiently.
        </p>
      </Card>

      {/* What We Offer */}
      <Card>
        <SectionTitle title="What We Offer" />
        <ul className="space-y-2 text-gray-600 list-disc list-inside">
          <li>Real-time analytics and reporting</li>
          <li>Revenue tracking and performance metrics</li>
          <li>Responsive and modern interface</li>
        </ul>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <h3 className="text-xl font-bold">10K+</h3>
          <p className="text-gray-500 text-sm">Active Users</p>
        </Card>
        <Card>
          <h3 className="text-xl font-bold">250+</h3>
          <p className="text-gray-500 text-sm">Companies</p>
        </Card>
        <Card>
          <h3 className="text-xl font-bold">99.9%</h3>
          <p className="text-gray-500 text-sm">Uptime</p>
        </Card>
      </div>
    </div>
  );
}

function SectionTitle({ title }) {
  return <h2 className="text-lg font-semibold mb-4">{title}</h2>;
}

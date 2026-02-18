import StatCard from "@/components/dashboard/StatCard";
import RecentActivity from "@/components/dashboard/RecentActivity";
import Projects from "@/components/dashboard/Projects";

export default function DashboardPage() {
  return (
    <div className="space-y-8 pt-10">
      
      {/* Stats Section */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value="2,300"
          badgeText="+5%"
          badgeVariant="success"
        />
        <StatCard
          title="Revenue"
          value="$53,000"
          badgeText="+8%"
          badgeVariant="success"
        />
        <StatCard
          title="Orders"
          value="1,200"
          badgeText="Pending"
          badgeVariant="warning"
        />
        <StatCard
          title="Issues"
          value="12"
          badgeText="High"
          badgeVariant="error"
        />
      </div>

      {/* Bottom Section */}
      <div className="grid md:grid-cols-2 gap-6">
        <Projects />
        <RecentActivity />
      </div>

    </div>
  );
}

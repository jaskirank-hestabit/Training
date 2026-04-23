import { Users, DollarSign, ShoppingCart, AlertCircle } from "lucide-react";
import StatCard from "@/components/dashboard/StatCard";
import SalesSection from "@/components/dashboard/SalesSection";
import ProjectsTable from "@/components/dashboard/ProjectsTable";
import OrdersOverview from "@/components/dashboard/OrdersOverview";

export default function DashboardPage() {
  return (
    <div className="space-y-8 pt-10">

      {/* Stats */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value="2,300"
          badgeText="+5%"
          badgeVariant="success"
          icon={Users}
        />
        <StatCard
          title="Revenue"
          value="$53,000"
          badgeText="+8%"
          badgeVariant="success"
          icon={DollarSign}
        />
        <StatCard
          title="Orders"
          value="1,200"
          badgeText="Pending"
          badgeVariant="warning"
          icon={ShoppingCart}
        />
        <StatCard
          title="Issues"
          value="12"
          badgeText="High"
          badgeVariant="error"
          icon={AlertCircle}
        />
      </div>

      {/* Sales + Active Users */}
      <SalesSection />

      {/* Projects + Orders */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ProjectsTable />
        </div>
        <OrdersOverview />
      </div>

    </div>
  );
}

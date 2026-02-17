import StatCard from "@/components/dashboard/StatCard";
import InfoCardsSection from "@/components/dashboard/InfoCardsSection";
import { FaWallet, FaUsers, FaUserPlus, FaShoppingCart } from "react-icons/fa";
import ProjectsOrdersSection from "@/components/dashboard/ProjectOrdersSection";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      
      {/* Stats Section */}
      <div className="grid gap-6 
                      grid-cols-1 
                      sm:grid-cols-2 
                      lg:grid-cols-4">

        <StatCard
          title="Today's Money"
          value="$53,000"
          percentage="+55%"
          isPositive
          icon={<FaWallet size={18} />}
        />

        <StatCard
          title="Today's Users"
          value="2,300"
          percentage="+5%"
          isPositive
          icon={<FaUsers size={18} />}
        />

        <StatCard
          title="New Clients"
          value="+3,052"
          percentage="-14%"
          isPositive={false}
          icon={<FaUserPlus size={18} />}
        />

        <StatCard
          title="Total Sales"
          value="$173,000"
          percentage="+8%"
          isPositive
          icon={<FaShoppingCart size={18} />}
        />
      </div>

      <InfoCardsSection />

      <ProjectsOrdersSection />

    </div>
  );
}

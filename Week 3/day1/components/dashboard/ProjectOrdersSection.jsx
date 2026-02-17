import Projects from "./Projects";
import OrdersOverview from "./OrdersOverview";

export default function ProjectsOrdersSection() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
      
      {/* 70% */}
      <div className="lg:col-span-7">
        <Projects />
      </div>

      {/* 30% */}
      <div className="lg:col-span-3">
        <OrdersOverview />
      </div>

    </div>
  );
}

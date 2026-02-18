import Link from "next/link";
import { LayoutDashboard, User, CreditCard } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="w-72 bg-white shadow-md p-6">
      <h2 className="text-lg font-bold text-teal-500 mb-6">
        Velora
      </h2>

      <nav className="flex flex-col gap-2 text-sm">
        <NavItem
          href="/dashboard"
          icon={LayoutDashboard}
          label="Dashboard"
        />

        <NavItem
          href="/dashboard/profile"
          icon={User}
          label="Profile"
        />

        <NavItem
          href="/about"
          icon={CreditCard}
          label="About"
        />
      </nav>
    </aside>
  );
}

function NavItem({ href, icon: Icon, label }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 transition"
    >
      <Icon size={18} className="text-teal-500" />
      <span className="text-gray-600">{label}</span>
    </Link>
  );
}

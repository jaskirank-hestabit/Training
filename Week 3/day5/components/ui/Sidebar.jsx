import Link from "next/link";
import { LayoutDashboard, User, CreditCard, FileText } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="w-72 bg-white shadow-md p-6">
      <Link href="/" className="inline-block mb-6">
        <h1 className="text-lg font-bold text-teal-500 hover:opacity-80 transition cursor-pointer">
          Velora
        </h1>
      </Link>

      <nav className="flex flex-col gap-2 text-sm">
        <NavItem href="/dashboard" icon={LayoutDashboard} label="Dashboard" />
        <NavItem href="/dashboard/profile" icon={User} label="Profile" />
        <NavItem href="/dashboard/users" icon={User} label="Users" />
        <NavItem href="/billing" icon={FileText} label="Billing" />
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

import Link from "next/link";
import Image from "next/image";
import {
  LayoutDashboard,
  Table,
  CreditCard,
  Repeat,
  User,
  LogIn,
  UserPlus,
} from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="w-72 flex flex-col p-6">
      {/* Logo */}
      <div className="pb-6 border-b flex justify-center">
        <Image
          src="/logo.png"
          alt="Logo"
          width={200}
          height={60}
          className="object-contain"
        />
      </div>

      {/* Navigation */}
      <nav className="mt-6 flex flex-col gap-1 text-sm">
        {/* Main Nav */}
        <SidebarItem icon={LayoutDashboard} label="Dashboard" active />
        <SidebarItem icon={Table} label="Tables" />
        <SidebarItem icon={CreditCard} label="Billing" />
        <SidebarItem icon={Repeat} label="RTL" />

        {/* Section Title */}
        <p className="mt-6 text-xs text-gray-400 uppercase">Account Pages</p>

        <SidebarItem icon={User} label="Profile" />
        <SidebarItem icon={LogIn} label="Sign In" />
        <SidebarItem icon={UserPlus} label="Sign Up" />
      </nav>

      {/* Sea Green Banner */}
      <div className="mt-20 bg-teal-400 rounded-xl p-5 text-white text-sm">
        <p className="font-semibold mb-2">Need help?</p>
        <p className="text-xs mb-4 opacity-90">Please check our docs</p>
        <button className="bg-white text-teal-500 text-xs font-medium px-4 py-2 rounded-lg">
          DOCUMENTATION
        </button>
      </div>
    </aside>
  );
}

/* Sidebar Item Component */
function SidebarItem({ icon: Icon, label, active }) {
  return (
    <Link
      href="#"
      className={`flex items-center gap-4 px-4 py-2 rounded-xl transition ${
        active
          ? "bg-gray-200"
          : "hover:bg-gray-100"
      }`}
    >
      {/* Icon Box */}
      <div
        className={`flex items-center justify-center w-8 h-8 rounded-lg ${
          active
            ? "bg-teal-500 border-teal-500"
            : "bg-white border-gray-200"
        }`}
      >
        <Icon
          size={18}
          className={`${
            active ? "text-white" : "text-teal-500"
          }`}
        />
      </div>

      {/* Text */}
      <span
        className={`text-sm ${
          active ? "text-black font-medium" : "text-gray-500"
        }`}
      >
        {label}
      </span>
    </Link>
  );
}


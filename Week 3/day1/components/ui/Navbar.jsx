import { Search, User, Settings, Bell } from "lucide-react";

export default function Navbar() {
  return (
    <header className="h-16 flex items-center justify-end px-8 pt-10">
      
      <div className="flex items-center gap-6">
        
        {/* Search */}
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            placeholder="Type here..."
            className="pl-9 pr-4 py-2 text-sm border rounded-full bg-gray-50 focus:outline-none focus:ring-2 focus:ring-teal-400"
          />
        </div>

        {/* Sign In */}
        <div className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer hover:text-black">
          <User size={16} />
          <span>Sign In</span>
        </div>

        {/* Settings */}
        <Settings size={18} className="text-gray-600 cursor-pointer hover:text-black" />

        {/* Notifications */}
        <Bell size={18} className="text-gray-600 cursor-pointer hover:text-black" />
      </div>

    </header>
  );
}

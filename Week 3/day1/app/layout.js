import "./globals.css";
import Navbar from "@/components/ui/Navbar";
import Sidebar from "@/components/ui/Sidebar";

export const metadata = {
  title: "Dashboard",
  description: "Dashboard Layout",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <div className="flex h-screen">
          
          {/* Sidebar */}
          <Sidebar />

          {/* Main Section */}
          <div className="flex-1 flex flex-col">
            
            {/* Navbar */}
            <Navbar />

            {/* Page Content */}
            <main className="flex-1 p-6">
              {children}
            </main>

          </div>
        </div>
      </body>
    </html>
  );
}

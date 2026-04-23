import "./globals.css";

export const metadata = {
  title: "Landing",
  description: "Landing Page",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        {children}
      </body>
    </html>
  );
}

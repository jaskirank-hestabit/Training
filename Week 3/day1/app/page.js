import LandingNavbar from "@/components/landing/LandingNavbar";
import HeroSection from "@/components/landing/HeroSection";
import FeaturesSection from "@/components/landing/FeaturesSection";
import TestimonialsSection from "@/components/landing/TestimonialsSection";
import LandingFooter from "@/components/landing/LandingFooter";

export const metadata = {
  title: "ProjectFlow - Manage Projects & Grow Revenue",
  description:
    "A powerful SaaS dashboard to track projects and grow your business.",
};

export default function HomePage() {
  return (
    <div className="bg-gradient-to-b from-[#041414] via-[#063c3c] to-[#0d7377] text-white">
      <LandingNavbar />
      <HeroSection />
      <FeaturesSection />
      <TestimonialsSection />
      <LandingFooter />
    </div>
  );
}

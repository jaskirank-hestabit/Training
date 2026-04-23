import Image from "next/image";
import Card from "@/components/ui/Card";

const features = [
  {
    title: "Project Tracking",
    desc: "Track project progress with real-time updates.",
    img: "/images/tracking.jpg",
  },
  {
    title: "Revenue Insights",
    desc: "Monitor earnings and analyze growth easily.",
    img: "/images/revenue.jpg",
  },
  {
    title: "Client Management",
    desc: "Build long-term client relationships.",
    img: "/images/clients.jpg",
  },
];

export default function FeaturesSection() {
  return (
    <section className="py-24">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white">Features</h2>
          <p className="text-gray-400 mt-4 max-w-2xl mx-auto">
            Everything you need to manage and grow faster.
          </p>
        </div>

        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="bg-white rounded-2xl overflow-hidden shadow-md hover:-translate-y-2 transition"
            >
              <div className="relative h-48 w-full">
                <Image
                  src={feature.img}
                  alt={feature.title}
                  fill
                  sizes="(max-width: 768px) 100vw, 33vw"
                  className="object-cover"
                />
              </div>

              <div className="p-6 text-center space-y-3">
                <h3 className="text-xl font-semibold text-gray-900">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm">
                  {feature.desc}
                </p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

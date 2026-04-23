import Card from "@/components/ui/Card";

const testimonials = [
  { text: "This dashboard transformed our workflow.", author: "Sarah K." },
  { text: "Revenue tracking has never been easier.", author: "James R." },
  { text: "Simple, modern and powerful.", author: "Emma L." },
];

export default function TestimonialsSection() {
  return (
    <section className="py-20">
      <div className="max-w-6xl mx-auto px-6 text-center space-y-12">
        <h2 className="text-3xl font-bold text-white">
          What Our Users Say
        </h2>

        <div className="grid gap-8 md:grid-cols-3">
          {testimonials.map((t, index) => (
            <Card
              key={index}
              className="bg-white rounded-2xl p-8 shadow-lg space-y-4"
            >
              <p className="text-gray-600 text-sm">“{t.text}”</p>
              <h4 className="font-semibold text-gray-900">
                — {t.author}
              </h4>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

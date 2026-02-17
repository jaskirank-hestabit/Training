import Image from "next/image";
import Link from "next/link";

export default function InfoCardsSection() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* LEFT CARD - Purity UI Dashboard */}
      <div
        className="bg-white rounded-2xl shadow-sm border border-gray-100 
                p-6 flex justify-between h-64"
      >
        {/* Left Text Area */}
        <div className="flex flex-col justify-between max-w-sm">
          {/* Top Content */}
          <div className="space-y-3">
            <p className="text-sm text-gray-400">Built by developers</p>

            <h2 className="text-xl font-bold text-gray-800">
              Purity UI Dashboard
            </h2>

            <p className="text-sm text-gray-500">
              From colors, cards, typography to complex elements, you will find
              the full documentation.
            </p>
          </div>

          {/* Bottom Link */}
          <Link
            href="#"
            className="text-sm font-medium text-gray-800 hover:underline"
          >
            Read more 
          </Link>
        </div>

        {/* Green Preview Box */}
        <div
          className="hidden sm:flex items-center justify-center 
                  w-48 rounded-xl 
                  bg-teal-400
                  text-white font-semibold text-lg"
        >
          chakra
        </div>
      </div>

      {/* RIGHT CARD - Work with the Rockets */}
      <div className="relative rounded-2xl overflow-hidden shadow-sm h-64">
        <Image
          src="/images/rockets.jpg" // put image in public/images
          alt="Work with the Rockets"
          width={800}
          height={200}
          className="w-full object-cover"
        />

        {/* Overlay */}
        <div className="absolute inset-0 bg-black/40 p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">
              Work with the Rockets
            </h2>

            <p className="text-sm text-gray-200 mt-2 max-w-sm">
              Wealth creation is an evolutionary recent positive-sum game. It is
              all about who take the opportunity first.
            </p>
          </div>

          <Link
            href="#"
            className="text-sm font-medium text-white hover:underline"
          >
            Read more 
          </Link>
        </div>
      </div>
    </div>
  );
}

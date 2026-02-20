"use client";

import Image from "next/image";

export default function ProfileHeader() {
  const name = "Jaskiran Kaur";
  const email = "jaskiran@email.com";

  const initials = name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase();

  return (
    <div className="relative">

      {/* Banner with Image */}
      <div className="relative h-40 md:h-52 rounded-xl overflow-hidden">
        <Image
          src="/images/signup-image.jpg"  // put image inside /public/images
          alt="Profile Banner"
          fill
          className="object-cover"
          priority
        />

        {/* Optional dark overlay */}
        <div className="absolute inset-0 bg-black/20"></div>
      </div>

      {/* Floating Profile Card */}
      <div className="relative -mt-12 px-4 md:px-8">
        <div className="bg-white rounded-2xl shadow-lg px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">

          {/* Left Section */}
          <div className="flex items-center gap-4">

            {/* Initials Avatar */}
            <div className="w-16 h-16 rounded-xl bg-teal-500 text-white flex items-center justify-center text-lg font-semibold shadow-md">
              {initials}
            </div>

            {/* Name + Email */}
            <div>
              <h2 className="text-base font-semibold text-gray-800">
                {name}
              </h2>
              <p className="text-sm text-gray-500">
                {email}
              </p>
            </div>
          </div>

          {/* Right Tabs */}
          <div className="flex items-center gap-2">
            <button className="px-4 py-2 text-sm font-medium rounded-lg bg-gray-100 text-gray-800 shadow-sm">
              Overview
            </button>

            <button className="px-4 py-2 text-sm font-medium rounded-lg text-gray-600 hover:bg-gray-100 transition">
              Projects
            </button>
          </div>

        </div>
      </div>

    </div>
  );
}

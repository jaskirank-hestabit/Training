"use client";

import Card from "@/components/ui/Card";
import { Users, MousePointerClick, ShoppingCart, Wrench } from "lucide-react";

export default function ActiveUsers() {
  const stats = [
    {
      label: "Users",
      value: "32,984",
      progress: 70,
      icon: Users,
    },
    {
      label: "Clicks",
      value: "2,42m",
      progress: 85,
      icon: MousePointerClick,
    },
    {
      label: "Sales",
      value: "2,400$",
      progress: 50,
      icon: ShoppingCart,
    },
    {
      label: "Items",
      value: "320",
      progress: 75,
      icon: Wrench,
    },
  ];

  return (
    <Card className="p-6 bg-white rounded-2xl shadow-sm">
      
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-800">
          Active Users
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          <span className="text-green-500 font-medium">(+23)</span>{" "}
          than last week
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;

          return (
            <div key={index} className="space-y-3">
              
              {/* Label + Icon */}
              <div className="flex items-center gap-3">
                <div className="bg-teal-500 p-2 rounded-lg text-white">
                  <Icon size={16} />
                </div>
                <span className="text-sm text-gray-500 font-medium">
                  {stat.label}
                </span>
              </div>

              {/* Value */}
              <p className="text-xl font-bold text-gray-800">
                {stat.value}
              </p>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-teal-500 h-1.5 rounded-full transition-all duration-700"
                  style={{ width: `${stat.progress}%` }}
                />
              </div>

            </div>
          );
        })}
      </div>
    </Card>
  );
}

"use client";

import Card from "@/components/ui/Card";
import {
  LineChart,
  Line,
  ResponsiveContainer,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import ActiveUsers from "./ActiveUsers";

const data = [
  { name: "Jan", sales: 200 },
  { name: "Feb", sales: 180 },
  { name: "Mar", sales: 300 },
  { name: "Apr", sales: 280 },
  { name: "May", sales: 350 },
  { name: "Jun", sales: 420 },
  { name: "Jul", sales: 390 },
];

export default function SalesSection() {
  return (
    <div className="grid lg:grid-cols-3 gap-6">
      
      {/* Sales Graph */}
      <div className="lg:col-span-2">
        <Card className="p-6 bg-white rounded-2xl shadow-sm">
          <h2 className="font-semibold mb-4">Sales Overview</h2>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="sales"
                  stroke="#14b8a6"
                  strokeWidth={3}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Active Users */}
      <ActiveUsers />
    </div>
  );
}

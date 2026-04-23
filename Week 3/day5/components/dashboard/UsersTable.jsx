"use client";

import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";

const users = [
  {
    id: 1,
    name: "Esthera Jackson",
    email: "esthera@simmmple.com",
    role: "Manager",
    department: "Organization",
    status: "Online",
    employed: "14/06/21",
  },
  {
    id: 2,
    name: "Alexa Liras",
    email: "alexa@simmmple.com",
    role: "Programmer",
    department: "Developer",
    status: "Offline",
    employed: "14/06/21",
  },
  {
    id: 3,
    name: "Laurent Michael",
    email: "laurent@simmmple.com",
    role: "Executive",
    department: "Projects",
    status: "Online",
    employed: "14/06/21",
  },
  {
    id: 4,
    name: "Daniel Thomas",
    email: "daniel@simmmple.com",
    role: "Programmer",
    department: "Developer",
    status: "Offline",
    employed: "14/06/21",
  },
];

export default function UsersTable() {
  return (
    <Card className="bg-white shadow-sm rounded-2xl overflow-hidden">
      <div className="p-6 border-b">
        <h2 className="text-lg font-semibold text-gray-800">
          Authors Table
        </h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left">
          <thead>
            <tr className="text-xs text-gray-400 uppercase border-b">
              <th className="px-6 py-4">Author</th>
              <th className="px-6 py-4">Function</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Employed</th>
              <th className="px-6 py-4"></th>
            </tr>
          </thead>

          <tbody>
            {users.map((user) => (
              <tr
                key={user.id}
                className="border-b last:border-none hover:bg-gray-50 transition"
              >
                {/* AUTHOR */}
                <td className="px-6 py-4 flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-400 to-cyan-400 flex items-center justify-center text-white font-semibold shadow-md">
                    {user.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-800">
                      {user.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {user.email}
                    </p>
                  </div>
                </td>

                {/* FUNCTION */}
                <td className="px-6 py-4">
                  <p className="text-sm font-semibold text-gray-700">
                    {user.role}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user.department}
                  </p>
                </td>

                {/* STATUS */}
                <td className="px-6 py-4">
                  <Badge
                    className={
                      user.status === "Online"
                        ? "bg-green-100 text-green-700 text-xs px-3 py-1 rounded-full"
                        : "bg-gray-200 text-gray-600 text-xs px-3 py-1 rounded-full"
                    }
                  >
                    {user.status}
                  </Badge>
                </td>

                {/* EMPLOYED */}
                <td className="px-6 py-4 text-sm text-gray-600">
                  {user.employed}
                </td>

                {/* ACTION */}
                <td className="px-6 py-4 text-sm font-medium text-indigo-600 hover:underline cursor-pointer">
                  Edit
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

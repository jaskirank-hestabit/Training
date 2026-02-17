import Card from "@/components/ui/Card";

export default function Projects() {
  const projects = [
    { name: "Chakra Soft UI Version", budget: "$14,000", progress: 60 },
    { name: "Add Progress Track", budget: "$3,000", progress: 10 },
    { name: "Fix Platform Errors", budget: "Not set", progress: 100 },
    { name: "Launch our Mobile App", budget: "$32,000", progress: 100 },
    { name: "Add the New Pricing Page", budget: "$400", progress: 25 },
    { name: "Redesign New Online Shop", budget: "$7,600", progress: 40 },
  ];

  return (
    <Card>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-800">Projects</h2>
        <p className="text-sm text-green-500">+30 done this month</p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-400 uppercase text-xs border-b">
              <th className="pb-3 text-left">Companies</th>
              <th className="pb-3 text-left">Budget</th>
              <th className="pb-3 text-left">Completion</th>
            </tr>
          </thead>

          <tbody>
            {projects.map((project, index) => (
              <tr key={index} className="border-b last:border-none">
                <td className="py-4 font-medium text-gray-700">
                  {project.name}
                </td>

                <td className="py-4 text-gray-600">
                  {project.budget}
                </td>

                <td className="py-4">
                  <div className="flex items-center gap-3">
                    <span className="text-teal-500 font-medium">
                      {project.progress}%
                    </span>

                    <div className="w-full bg-gray-200 h-2 rounded-full">
                      <div
                        className="bg-teal-400 h-2 rounded-full"
                        style={{ width: `${project.progress}%` }}
                      />
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

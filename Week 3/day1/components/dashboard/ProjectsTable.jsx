import Card from "@/components/ui/Card";

export default function ProjectsTable() {
  const projects = [
    { name: "Chakra Soft UI Version", budget: "$14,000", completion: 60 },
    { name: "Add Progress Track", budget: "$3,000", completion: 10 },
    { name: "Fix Platform Errors", budget: "Not set", completion: 100 },
  ];

  return (
    <Card className="p-6 bg-white rounded-2xl shadow-sm">
      <h2 className="font-semibold mb-4">Projects</h2>

      <table className="w-full text-sm">
        <thead className="text-gray-400 border-b">
          <tr>
            <th className="text-left pb-3">Companies</th>
            <th className="text-left pb-3">Budget</th>
            <th className="text-left pb-3">Completion</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((project, i) => (
            <tr key={i} className="border-b last:border-none">
              <td className="py-3 font-medium">{project.name}</td>
              <td>{project.budget}</td>
              <td>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className="bg-teal-500 h-2 rounded-full"
                    style={{ width: `${project.completion}%` }}
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

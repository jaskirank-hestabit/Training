import Card from "@/components/ui/Card";

export default function Projects() {
  const projects = [
    { name: "Website Redesign", status: "In Progress" },
    { name: "Mobile App", status: "Completed" },
    { name: "Admin Dashboard", status: "Pending" },
  ];

  return (
    <Card>
      <h2 className="font-semibold mb-4">Projects</h2>

      <div className="space-y-3 text-sm">
        {projects.map((project, index) => (
          <div
            key={index}
            className="flex justify-between border-b pb-2 last:border-none"
          >
            <span>{project.name}</span>
            <span className="text-gray-500">{project.status}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

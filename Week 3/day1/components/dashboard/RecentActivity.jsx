import Card from "@/components/ui/Card";

export default function RecentActivity() {
  const activities = [
    "New user registered",
    "Server payment completed",
    "New order received",
    "Profile updated",
  ];

  return (
    <Card>
      <h2 className="font-semibold mb-4">Recent Activity</h2>

      <ul className="space-y-3 text-sm text-gray-600">
        {activities.map((item, index) => (
          <li key={index} className="border-b pb-2 last:border-none">
            {item}
          </li>
        ))}
      </ul>
    </Card>
  );
}

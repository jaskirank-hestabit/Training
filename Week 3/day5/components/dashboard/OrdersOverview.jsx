import Card from "@/components/ui/Card";

export default function OrdersOverview() {
  const orders = [
    "New order #4219423",
    "Server payments for April",
    "New card added",
    "Unlock packages for Development",
  ];

  return (
    <Card className="p-6 bg-white rounded-2xl shadow-sm">
      <h2 className="font-semibold mb-4">Orders Overview</h2>

      <ul className="space-y-4 text-sm text-gray-600">
        {orders.map((order, index) => (
          <li key={index} className="border-b pb-2 last:border-none">
            {order}
          </li>
        ))}
      </ul>
    </Card>
  );
}

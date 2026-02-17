export default function OrdersOverview() {
  const orders = [
    { title: "$2400, Design changes", date: "22 DEC 7:20 PM" },
    { title: "New order #4219423", date: "21 DEC 11:21 PM" },
    { title: "Server Payments for April", date: "21 DEC 9:28 PM" },
    { title: "New card added for order #3210145", date: "20 DEC 3:52 PM" },
    { title: "Unlock packages for Development", date: "19 DEC 11:35 PM" },
    { title: "New order #9851258", date: "18 DEC 4:41 PM" },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-800">
          Orders overview
        </h2>
        <p className="text-sm text-green-500">+30% this month</p>
      </div>

      <div className="space-y-5">
        {orders.map((order, index) => (
          <div key={index} className="border-l-2 border-gray-200 pl-4">
            <p className="text-sm font-medium text-gray-700">
              {order.title}
            </p>
            <p className="text-xs text-gray-400">
              {order.date}
            </p>
          </div>
        ))}
      </div>

    </div>
  );
}

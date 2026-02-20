import Card from "@/components/ui/Card";

export default function PaymentsTable() {
  const payments = [
    { method: "Visa **** 4242", date: "Feb 10, 2026", amount: "$200" },
    { method: "Mastercard **** 8754", date: "Jan 14, 2026", amount: "$320" },
    { method: "UPI", date: "Dec 22, 2025", amount: "$150" },
  ];

  return (
    <Card>
      <h2 className="text-lg font-semibold mb-4">Payments Made</h2>

      <table className="w-full text-sm">
        <thead className="text-gray-500 text-left">
          <tr>
            <th className="pb-2">Method</th>
            <th className="pb-2">Date</th>
            <th className="pb-2">Amount</th>
          </tr>
        </thead>

        <tbody>
          {payments.map((payment, index) => (
            <tr key={index} className="border-t">
              <td className="py-3">{payment.method}</td>
              <td>{payment.date}</td>
              <td>{payment.amount}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

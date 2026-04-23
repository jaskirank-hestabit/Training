import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";

export default function InvoicesTable() {
  const invoices = [
    { id: "INV-001", amount: "$120", status: "Paid" },
    { id: "INV-002", amount: "$250", status: "Pending" },
    { id: "INV-003", amount: "$430", status: "Overdue" },
  ];

  const statusVariant = {
    Paid: "success",
    Pending: "warning",
    Overdue: "error",
  };

  return (
    <Card>
      <h2 className="text-lg font-semibold mb-4">Invoices</h2>

      <table className="w-full text-sm">
        <thead className="text-gray-500 text-left">
          <tr>
            <th className="pb-2">Invoice</th>
            <th className="pb-2">Amount</th>
            <th className="pb-2">Status</th>
          </tr>
        </thead>

        <tbody>
          {invoices.map((invoice) => (
            <tr key={invoice.id} className="border-t">
              <td className="py-3">{invoice.id}</td>
              <td>{invoice.amount}</td>
              <td>
                <Badge variant={statusVariant[invoice.status]}>
                  {invoice.status}
                </Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

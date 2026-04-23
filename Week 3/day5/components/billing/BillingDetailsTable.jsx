import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

export default function BillingDetailsTable() {
  const billingAccounts = [
    {
      company: "Velora Technologies",
      email: "billing@velora.com",
      vat: "FRB123456",
    },
    {
      company: "Velora International",
      email: "finance@velora.com",
      vat: "FRB987654",
    },
  ];

  return (
    <Card>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Billing Details</h2>
        <Button size="sm">Add New</Button>
      </div>

      <table className="w-full text-sm">
        <thead className="text-gray-500 text-left">
          <tr>
            <th className="pb-2">Company</th>
            <th className="pb-2">Email</th>
            <th className="pb-2">VAT Number</th>
            <th className="pb-2 text-right">Actions</th>
          </tr>
        </thead>

        <tbody>
          {billingAccounts.map((account, index) => (
            <tr key={index} className="border-t">
              <td className="py-3 font-medium">{account.company}</td>
              <td>{account.email}</td>
              <td>{account.vat}</td>
              <td className="text-right space-x-2">
                <Button variant="outline" size="sm">
                  Edit
                </Button>
                <Button variant="danger" size="sm">
                  Delete
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

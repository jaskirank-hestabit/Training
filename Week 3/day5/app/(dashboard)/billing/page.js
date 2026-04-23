import Button from "@/components/ui/Button";
import InvoicesTable from "@/components/billing/InvoicesTable";
import PaymentsTable from "@/components/billing/PaymentsTable";
import BillingDetailsTable from "@/components/billing/BillingDetailsTable";

export default function BillingPage() {
  return (
    <div className="p-8 space-y-8">

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Billing</h1>
          <p className="text-gray-500 text-sm">
            Manage invoices, payments and billing details.
          </p>
        </div>
      </div>

      {/* Row 1 */}
      <div className="grid lg:grid-cols-2 gap-6">
        <InvoicesTable />
        <PaymentsTable />
      </div>

      {/* Row 2 Full Width */}
      <BillingDetailsTable />

    </div>
  );
}

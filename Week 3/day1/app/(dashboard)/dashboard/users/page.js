import UsersTable from "@/components/dashboard/UsersTable";

export default function UsersPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">
          Tables
        </h1>
      </div>

      <UsersTable />
    </div>
  );
}

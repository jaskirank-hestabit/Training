import Card from "@/components/ui/Card";

export default function ProfileInfo() {
  return (
    <Card>
      <h2 className="font-semibold mb-4">Profile Information</h2>

      <p className="text-sm text-gray-500 mb-4">
        Hi, I am Jaskiran. This is a simple dashboard profile page built
        using reusable components.
      </p>

      <div className="text-sm space-y-2">
        <InfoRow label="Full Name" value="Jaskiran Kaur" />
        <InfoRow label="Mobile" value="+91 12345 67890" />
        <InfoRow label="Email" value="example@email.com" />
        <InfoRow label="Location" value="India" />
      </div>
    </Card>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-400">{label}:</span>
      <span className="text-gray-700 font-medium">{value}</span>
    </div>
  );
}

import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

export default function EditProfileForm() {
  return (
    <Card className="space-y-4">
      <h2 className="font-semibold">Edit Profile</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input label="Full Name" placeholder="Jaskiran Kaur" />
        <Input label="Email" type="email" placeholder="example@email.com" />
        <Input label="Location" placeholder="India" />
        <Input label="Phone" placeholder="+91 12345 67890" />
      </div>

      <Button className="mt-4">Save Changes</Button>
    </Card>
  );
}

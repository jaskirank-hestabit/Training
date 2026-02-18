import PlatformSettings from "@/components/profile/PlatformSettings";
import ProfileInfo from "@/components/profile/ProfileInfo";
import EditProfileForm from "@/components/profile/EditProfileForm";

export default function ProfilePage() {
  return (
    <div className="space-y-8 pt-4">
      <h1 className="text-2xl font-bold">Profile</h1>

      {/* Top Two Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <PlatformSettings />
        <ProfileInfo />
      </div>

      {/* Edit Profile Section */}
      <EditProfileForm />
    </div>
  );
}

import PlatformSettings from "@/components/profile/PlatformSettings";
import ProfileInfo from "@/components/profile/ProfileInfo";
import EditProfileForm from "@/components/profile/EditProfileForm";
import ProfileHeader from "@/components/profile/ProfileHeader";

export default function ProfilePage() {
  return (
    <div className="space-y-8">

      {/* Banner + Avatar */}
      <ProfileHeader />

      {/* Two Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ProfileInfo />
        <PlatformSettings />
      </div>

      {/* Edit Form */}
      <EditProfileForm />
    </div>
  );
}

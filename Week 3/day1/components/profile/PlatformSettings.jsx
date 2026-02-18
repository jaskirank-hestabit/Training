import Card from "@/components/ui/Card";
import Switch from "@/components/ui/Switch";

export default function PlatformSettings() {
  return (
    <Card>
      <h2 className="font-semibold mb-4">Platform Settings</h2>

      <div className="space-y-6 text-sm">
        <div>
          <p className="text-gray-400 text-xs mb-3">ACCOUNT</p>

          <SettingRow
            label="Email me when someone follows me"
            checked
          />
          <SettingRow
            label="Email me when someone answers on my post"
          />
          <SettingRow
            label="Email me when someone mentions me"
            checked
          />
        </div>
      </div>
    </Card>
  );
}

function SettingRow({ label, checked }) {
  return (
    <div className="flex items-center justify-between py-2">
      <span className="text-gray-600">{label}</span>
      <Switch checked={checked} />
    </div>
  );
}

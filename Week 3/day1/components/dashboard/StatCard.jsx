import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";

export default function StatCard({ title, value, badgeText, badgeVariant }) {
  return (
    <Card>
      <h3 className="text-sm text-gray-500">{title}</h3>
      <p className="text-2xl font-bold mt-1">{value}</p>
      {badgeText && (
        <div className="mt-2">
          <Badge variant={badgeVariant}>{badgeText}</Badge>
        </div>
      )}
    </Card>
  );
}

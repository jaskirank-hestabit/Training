import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";

export default function StatCard({
  title,
  value,
  badgeText,
  badgeVariant,
  icon: Icon,
}) {
  return (
    <Card className="relative p-6 bg-white rounded-2xl shadow-sm">
      
      {/* Icon */}
      {Icon && (
        <div className="absolute top-6 right-6 bg-teal-500 p-3 rounded-xl text-white">
          <Icon size={18} />
        </div>
      )}

      {/* Title */}
      <h3 className="text-sm text-gray-500">{title}</h3>

      {/* Value + Badge in same row */}
      <div className="flex items-center gap-3 mt-2">
        <p className="text-2xl font-bold text-gray-800">
          {value}
        </p>

        {badgeText && (
          <Badge variant={badgeVariant}>
            {badgeText}
          </Badge>
        )}
      </div>

    </Card>
  );
}

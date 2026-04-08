import { useStockLevels, useLowStock } from "@/hooks/useStock";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";
import {
  AlertTriangle,
  Package,
  TrendingDown,
  CheckCircle,
} from "lucide-react";

// KPI card command
const KpiCard = ({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
}) => (
  <div className="bg-white rounded-xl border broder-gray-200 p-6 flex items-center gap-4">
    <div className={`p-3 rounded-lg ${color}`}>{icon}</div>
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
    </div>
  </div>
);

export const DashboardPage = () => {
  const { data: stockData } = useStockLevels();
  const { data: lowStockItems } = useLowStock();

  const totalProducts = stockData?.meta.total_count ?? 0;
  const lowCount = lowStockItems?.length ?? 0;
  const outCount =
    stockData?.data.filter((s) => s.stock_status === "OUT").length ?? 0;
  const okCount = totalProducts - lowCount - outCount;

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Real-time inventory overview" />

      {/* KPI cards */}
      <div className="grid gird-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KpiCard
          label="Total Products"
          value={totalProducts}
          icon={<Package size={20} className="text-blue-600" />}
          color="bg-blue-50"
        />
        <KpiCard
          label="OK Stock"
          value={okCount}
          icon={<CheckCircle size={20} className="text-green-600" />}
          color="bg-green-50"
        />
        <KpiCard
          label="Low Stock"
          value={lowCount}
          icon={<TrendingDown size={20} className="text-yellow-600" />}
          color="bg-yellow-50"
        />
        <KpiCard
          label="Out of Stock"
          value={outCount}
          icon={<AlertTriangle size={20} className="text-red-600" />}
          color="bg-red-50"
        />
      </div>

        {/* Low Stock alert table */}
        {lowCount > 0 && (
            <div className="bg-white rounded-xl border border-gray-200">
                <div className="px-6 py-4 border-b border-gray-20à">
                    <h2 className="font-semibold text-gray-800">
                        Items Needing Attention
                    </h2>
                </div>
                <div className="divide-y divide-gray-100">
                    {lowStockItems?.map(item => (
                        <div key={item.id} className="px-6 py-4 flex items-center justify-between">
                            <div>
                                <p className="font-medium text-gray-800">{item.product.name}</p>
                                <p className="text-sm text-gray-500">{item.product.sku}</p>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="text-sm text-gray-600">
                                    {item.quantity_on_hand} {item.product.unit_of_measure} available
                                </span>
                                <StatusBadge status={item.stock_status} />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        )}

    </div>
  );
};

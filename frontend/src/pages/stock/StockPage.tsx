import { useState } from "react";
import { useStockLevels } from "@/hooks/useStock";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";

export const StockPage = () => {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useStockLevels();

  const filtered =
    data?.data.filter(
      (item) =>
        item.product.name.toLowerCase().includes(search.toLowerCase()) ||
        item.product.sku.toLowerCase().includes(search.toLowerCase()),
    ) ?? [];

  return (
    <div>
      <PageHeader
        title="Stock Levels"
        subtitle="Current inventory across all locations"
      />

      {/* Searc */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search by product name or SKU..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-sm px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {[
                "Product",
                "SKU",
                "Location",
                "On Hand",
                "Available",
                "Reorder Point",
                "Status",
              ].map((h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                  Loading Stock levels
                </td>
              </tr>
            ) : (
              filtered.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">
                    {item.product.name}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {item.product.sku}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {item.location_name}
                  </td>
                  <td className="px-4 py-3">{item.quantity_on_hand}</td>
                  <td className="px-4 py-3 font-medium">
                    {item.quantity_on_hand}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {item.reorder_point}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={item.stock_status} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

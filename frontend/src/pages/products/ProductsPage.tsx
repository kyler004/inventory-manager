import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { productsApi } from "@/api/products.api";
import { PageHeader } from "@/components/common/PageHeader";
import { Plus } from "lucide-react";

export const ProductsPage = () => {
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["products", { search }],
    queryFn: () => productsApi.getProducts({ search }),
  });

  return (
    <div>
      <PageHeader
        title="Products"
        subtitle={`${data?.meta.total_count ?? 0} products in catalog`}
        action={
          <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors">
            <Plus size={16} />
            Add Product
          </button>
        }
      />

      <div className="mb-4">
        <input
          type="text"
          placeholder="Search by name, SKU or barcode..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-sw-sm px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {[
                "Name",
                "SKU",
                "Category",
                "Unit",
                "Cost",
                "Retail",
                "Margin",
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
                <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                  Loading products...
                </td>
              </tr>
            ) : (
              data?.data.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">
                    {product.name}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{product.sku}</td>
                  <td className="px-4 py-3 text-gray-500">
                    {product.category_name}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {product.unit_of_measure}
                  </td>
                  <td className="px-4 py-3">${product.unit_price_cost}</td>
                  <td className="px-4 py-3">${product.unit_price_retail}</td>
                  <td className="px-4 py-3 text-green-600">
                    {product.margin.toFixed(1)}%
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        product.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-500"
                      }`}
                    >
                      {product.is_active ? "Active" : "Inactive"}
                    </span>
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

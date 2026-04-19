import { useState } from 'react'
import { PageHeader } from '@/components/common/PageHeader'
import { useStockValuation, useShrinkage, useTurnover, useDeadStock } from '@/hooks/useReports'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'

// Tab type
type ReportTab = 'valuation' | 'shrinkage' | 'turnover' | 'dead-stock'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export const ReportsPage = () => {
  const [activeTab, setActiveTab] = useState<ReportTab>('valuation')

  const { data: valuation, isLoading: loadingValuation } =
    useStockValuation()
  const { data: shrinkage, isLoading: loadingShrinkage } =
    useShrinkage()
  const { data: turnover, isLoading: loadingTurnover } =
    useTurnover({ days: 30 })
  const { data: deadStock, isLoading: loadingDeadStock } =
    useDeadStock({ days: 30 })

  const tabs: { key: ReportTab; label: string }[] = [
    { key: 'valuation',  label: 'Stock Valuation' },
    { key: 'shrinkage',  label: 'Shrinkage' },
    { key: 'turnover',   label: 'Turnover' },
    { key: 'dead-stock', label: 'Dead Stock' },
  ]

  return (
    <div>
      <PageHeader
        title="Reports & Analytics"
        subtitle="Data-driven inventory insights"
      />

      {/* Tab navigation */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Stock Valuation ─────────────────────────── */}
      {activeTab === 'valuation' && (
        <div className="space-y-6">
          {/* KPI totals */}
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: 'Total Cost Value', value: valuation?.totals?.total_cost_value, prefix: '$' },
              { label: 'Total Retail Value', value: valuation?.totals?.total_retail_value, prefix: '$' },
              { label: 'Total Products', value: valuation?.totals?.total_products, prefix: '' },
            ].map(kpi => (
              <div key={kpi.label} className="bg-white rounded-xl border border-gray-200 p-6">
                <p className="text-sm text-gray-500">{kpi.label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {loadingValuation ? '...' : `${kpi.prefix}${Number(kpi.value ?? 0).toLocaleString()}`}
                </p>
              </div>
            ))}
          </div>

          {/* By category chart */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-800 mb-4">
              Stock Value by Category
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={valuation?.by_category ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="product__category__name"
                  tick={{ fontSize: 12 }}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(value: number) =>
                    [`$${value.toLocaleString()}`, 'Cost Value']
                  }
                />
                <Bar
                  dataKey="total_cost_value"
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* ── Shrinkage ───────────────────────────────── */}
      {activeTab === 'shrinkage' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <p className="text-sm text-gray-500">Total Incidents</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {loadingShrinkage ? '...' : shrinkage?.totals?.total_incidents ?? 0}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <p className="text-sm text-gray-500">Total Loss Value</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                ${Number(shrinkage?.totals?.total_loss_value ?? 0).toLocaleString()}
              </p>
            </div>
          </div>

          {/* By reason pie chart */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-800 mb-4">
              Loss by Reason
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={shrinkage?.by_reason ?? []}
                  dataKey="total_loss_value"
                  nameKey="reason"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ reason, percent }) =>
                    `${reason} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {(shrinkage?.by_reason ?? []).map((_: any, i: number) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => [`$${value.toFixed(2)}`, 'Loss']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Top shrinking products */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-800">
                Top 10 Products by Loss
              </h3>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  {['Product', 'SKU', 'Incidents', 'Units Lost', 'Value Lost'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {(shrinkage?.by_product ?? []).map((row: any) => (
                  <tr key={row.product__sku} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{row.product__name}</td>
                    <td className="px-4 py-3 text-gray-500">{row.product__sku}</td>
                    <td className="px-4 py-3">{row.total_incidents}</td>
                    <td className="px-4 py-3">{row.total_loss_quantity}</td>
                    <td className="px-4 py-3 text-red-600 font-medium">
                      ${Number(row.total_loss_value).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Turnover ────────────────────────────────── */}
      {activeTab === 'turnover' && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800">
              Inventory Turnover — Last 30 Days
            </h3>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                {['Product', 'SKU', 'Units Sold', 'Avg Stock', 'Turnover Rate'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loadingTurnover ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : (turnover?.products ?? []).map((row: any) => (
                <tr key={row.product_sku} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{row.product_name}</td>
                  <td className="px-4 py-3 text-gray-500">{row.product_sku}</td>
                  <td className="px-4 py-3">{row.units_sold}</td>
                  <td className="px-4 py-3">{row.avg_stock_level}</td>
                  <td className="px-4 py-3">
                    <span className={`font-medium ${
                      row.turnover_rate > 2
                        ? 'text-green-600'
                        : row.turnover_rate > 1
                        ? 'text-yellow-600'
                        : 'text-red-600'
                    }`}>
                      {row.turnover_rate}x
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Dead Stock ──────────────────────────────── */}
      {activeTab === 'dead-stock' && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <p className="text-sm text-gray-500">
              Total Dead Stock Value (no movement in 30 days)
            </p>
            <p className="text-3xl font-bold text-red-600 mt-1">
              ${Number(deadStock?.total_dead_stock_value ?? 0).toLocaleString()}
            </p>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  {['Product', 'Category', 'Location', 'Qty on Hand', 'Value'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {loadingDeadStock ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                      Loading...
                    </td>
                  </tr>
                ) : (deadStock?.items ?? []).map((item: any, i: number) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{item.product__name}</td>
                    <td className="px-4 py-3 text-gray-500">{item.product__category__name}</td>
                    <td className="px-4 py-3 text-gray-500">{item.location__name}</td>
                    <td className="px-4 py-3">{item.quantity_on_hand}</td>
                    <td className="px-4 py-3 font-medium text-red-600">
                      ${Number(item.stock_value).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
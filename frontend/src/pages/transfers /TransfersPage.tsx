import { useTransfers, useApproveTransfer, useDispatchTransfer } from '@/hooks/useTransfer'
import { PageHeader } from '@/components/common/PageHeader'
import { useAuthStore } from '@/store/authStore'
import { Plus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import type { TransferStatus } from '@/types/transfer.types'

const statusColors: Record<TransferStatus, string> = {
  requested:   'bg-gray-100 text-gray-600',
  approved:    'bg-blue-100 text-blue-600',
  in_transit:  'bg-yellow-100 text-yellow-700',
  completed:   'bg-green-100 text-green-600',
  cancelled:   'bg-red-100 text-red-500',
}

export const TransfersPage = () => {
  const { data, isLoading } = useTransfers()
  const approveTransfer = useApproveTransfer()
  const dispatchTransfer = useDispatchTransfer()
  const user = useAuthStore(state => state.user)

  const isWarehouseOrAbove = user?.role === 'Admin' || user?.role === 'WarehouseManager'

  return (
    <div>
      <PageHeader
        title="Stock Transfers"
        subtitle="Move stock between locations"
        action={
          <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium">
            <Plus size={16} />
            Request Transfer
          </button>
        }
      />

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['#', 'From', 'To', 'Status', 'Requested By', 'Created', 'Actions'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                  Loading transfers...
                </td>
              </tr>
            ) : data?.data?.map(transfer => (
              <tr key={transfer.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-blue-600">
                  TRF-{String(transfer.id).padStart(4, '0')}
                </td>
                <td className="px-4 py-3 text-gray-800">
                  {transfer.from_location_name}
                </td>
                <td className="px-4 py-3 text-gray-800">
                  {transfer.to_location_name}
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${statusColors[transfer.status]}`}>
                    {transfer.status.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {transfer.requested_by_name}
                </td>
                <td className="px-4 py-3 text-gray-400 text-xs">
                  {formatDistanceToNow(new Date(transfer.created_at), {
                    addSuffix: true
                  })}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">

                    {/* Approve — warehouse manager only */}
                    {transfer.status === 'requested' && isWarehouseOrAbove && (
                      <button
                        onClick={() => approveTransfer.mutate(transfer.id)}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Approve
                      </button>
                    )}

                    {/* Dispatch — warehouse manager only */}
                    {transfer.status === 'approved' && isWarehouseOrAbove && (
                      <button
                        onClick={() => dispatchTransfer.mutate(transfer.id)}
                        className="text-xs text-green-600 hover:underline"
                      >
                        Dispatch
                      </button>
                    )}

                    {/* In transit label */}
                    {transfer.status === 'in_transit' && (
                      <span className="text-xs text-yellow-600">
                        Awaiting receipt
                      </span>
                    )}

                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
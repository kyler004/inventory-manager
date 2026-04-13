import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '@/components/common/PageHeader'
import { Plus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import client from '@/api/client'


const statusColors: Record<string, string> = {
  draft:               'bg-gray-100 text-gray-600',
  sent:                'bg-blue-100 text-blue-600',
  confirmed:           'bg-purple-100 text-purple-600',
  partially_received:  'bg-yellow-100 text-yellow-600',
  received:            'bg-green-100 text-green-600',
  cancelled:           'bg-red-100 text-red-600',
}

export const PurchaseOrdersPage = () => {
    const { data, isLoading } = useQuery({
        queryKey: ['purchase-orders'], 
        queryFn: async () => {
            const res = await client.get('/purchase-orders/')
            return res.data
        }
    })

    return (
        <div>
            <PageHeader
                title='Purchase Orders'
                subtitle='Manage procurement from suppliers'
                action={
                    <button className='flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium'>
                        <Plus size={16} />
                        New Order
                    </button>
                }
            />

            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            {['PO Number', 'Supplier', 'Destination', 'Status', 'Expected', 'Total', 'Created'].map(h => (
                                <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                {h}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className='divide-y divide-gray-100'>
                        {isLoading ? (
                            <tr>
                                <td colSpan={7} className='x-4 py-8 text-center text-gray-500'>
                                    Loading purchase orders...
                                </td>
                            </tr>
                        ): data?.data?.map((po: any) => (
                            <tr key={po.id} className='hover:bg-gray-50 cursor-pointer'>
                                <td className='px-4 py-3 font-medium text-blue-600'>
                                    PO-{String(po.id).padStart(5, '0')}
                                </td>
                                <td className="px-5 py-3 text-gray-800">{po.supplier_name}</td>
                                <td className="px-5 py-3 text-gray-500">{po.destination_name}</td>
                                <td className="px-4 py-3">
                                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${statusColors[po.status]}`}>
                                        {po.status.replace('_', '')}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-gray-500">
                                    {po.expected_delivery_date ?? '—'}
                                </td>
                                <td className='px-4 py-3 font-medium'>
                                    ${Number(po.total_amount).toFixed(2)}
                                </td>
                                <td className="px-4 py-3 text-gray-400 text-xs">
                                    {formatDistanceToNow(new Date(po.created_at), { addSuffix: true})}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
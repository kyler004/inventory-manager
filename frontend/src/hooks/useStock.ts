import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { stockApi } from '@/api/stock.api'
import { StockAdjustment } from '@/types/stock.types'
import toast from 'react-hot-toast'

// Query keys — centralized so invalidation is consistent
export const stockKeys = {
  all: ['stock'] as const,
  levels: (filters?: Record<string, unknown>) =>
    [...stockKeys.all, 'levels', filters] as const,
  low: () => [...stockKeys.all, 'low'] as const,
  movements: (filters?: Record<string, unknown>) =>
    [...stockKeys.all, 'movements', filters] as const,
}

export const useStockLevels = (filters?: Record<string, unknown>) =>
  useQuery({
    queryKey: stockKeys.levels(filters),
    queryFn: () => stockApi.getStockLevels(filters),
  })

export const useLowStock = (locationId?: number) =>
  useQuery({
    queryKey: stockKeys.low(),
    queryFn: () => stockApi.getLowStock(locationId),
  })

export const useAdjustStock = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: StockAdjustment) => stockApi.adjustStock(data),
    onSuccess: () => {
      // Invalidate stock queries so tables refresh automatically
      queryClient.invalidateQueries({ queryKey: stockKeys.all })
      toast.success('Stock adjusted successfully')
    },
    onError: () => {
      toast.error('Failed to adjust stock. Please try again.')
    },
  })
}
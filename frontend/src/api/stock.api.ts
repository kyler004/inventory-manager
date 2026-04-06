import client from './client'
import type { StockLevel, StockAdjustment } from '@/types/stock.types'
import type { PaginatedResponse, ApiResponse } from '@/types/api.types'

export const stockApi = {
    getStockLevels: async (params?: Record<string, unknown>) => {
        const response = await client.get<PaginatedResponse<StockLevel>>(
            '/stock/', 
            { params }
        )
        return response.data
    }, 

    getLowStock: async (locationId?: number) => {
        const response = await client.get<ApiResponse<StockLevel[]>>(
            '/stock/low/', 
            { params: { location: locationId }}
        )
        return response.data.data
    }, 

    adjustStock: async (data: StockAdjustment) => {
        const response = await client.post('/stock/adjustments/', data)
        return response.data.data
    }, 

    getMovements: async (params?: Record<string, unknown>) => {
        const response = await client.get('/stock/movements/', {params })
        return response.data
    }
}
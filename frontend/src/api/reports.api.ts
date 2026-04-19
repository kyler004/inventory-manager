import client from './client'

export const reportsApi = {
    getStockValuation: async (params?: Record<string, unknown>) => {
        const response = await client.get('/reports/stock-valuation/', { params })
        return response.data.data
    }, 

    getShrinkage: async (params?: Record<string, unknown>) => {
        const response = await client.get('/report/shrinkage/', { params })
        return response.data.data
    },

    getTurnover: async (params?: Record<string, unknown>) => {
        const response = await client.get('/reports/turnover/', { params })
        return response.data.data
    },

    getDeadStock: async (params?: Record<string, unknown>) => {
        const response = await client.get('/reports/dead-stock/', { params })
        return response.data.data
    }, 

    getSupplierPerformance: async (params?: Record<string, unknown>) => {
        const response  = await client.get('/reports/supplier-performance/', { params })
        return response.data.data
    }
}
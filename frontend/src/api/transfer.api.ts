import client from "./client";
import type { PaginatedResponse, ApiResponse } from "@/types/api.types";
import type { StockTransfer } from "@/types/transfer.types";

export const transferApi = {
    getTransfers: async (params?: Record <string, unknown>) => {
        const response = await client.get<PaginatedResponse<StockTransfer>>(
            '/transfers/', 
            { params }
        )

        return response.data
    }, 

    getTransfer: async (id: number) => {
        const response = await client.get<ApiResponse<StockTransfer>>(
            `/transfers/${id}/`
        )

        return response.data
    },

    createTransfer: async (data: Partial<StockTransfer>) => {
        const response = await client.post<ApiResponse<StockTransfer>>(
            '/transfers/', 
            data
        )

        return response.data.data
    }, 

    approve: async (id:number) => {
        const response = await client.post(`/transfers/${id}/approve`)
        return response.data.data
    }, 

    dispatch: async(id: number) => {
        const response = await client.post(`/transfers/${id}/dispatch`)
        return response.data.data
    }, 

    receive: async(id: number, items: { product_id: number, quantity_received: number }[]) => {
        const response = await client.post(`/transfers/${id}/receive/`, { items })
        return response.data.data
    }, 

    cancel: async (id: number) => {
        const response = await client.post(`/transfers/${id}/cancel`)
        return response.data.data
    }
}
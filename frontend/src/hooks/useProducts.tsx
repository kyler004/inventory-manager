import { useQuery , useMutation, useQueryClient } from '@tanstack/react-query'
import { productsApi } from '@/api/products.api'
import type { Product } from '@/types/product.types'
import toast from 'react-hot-toast'

export const productKeys = {
    all: ['products'] as const, 
    list: (filters?: Record<string, unknown>) => 
        [...productKeys.all, 'list', filters] as const, 
    detail: (id: number) => 
        [...productKeys.all, 'detail', id] as const, 
}

export const useProducts = (filters?: Record<string, unknown>) => 
    useQuery ({
        queryKey: productKeys.list(filters), 
        queryFn: () => productsApi.getProducts(filters), 
    })

export const useProduct = (id: number) => 
    useQuery({
        queryKey: productKeys.detail(id), 
        queryFn: () => productsApi.getProduct(id), 
        enabled: !!id, // Only fetch is id exists
    })

export const useCreateProduct = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (data: Partial<Product>) => productsApi.createProduct(data), 
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: productKeys.all })
            toast.success('Product created successfully')
        }, 
        onError: () => {
            toast.error('Failed to create the product')
        }, 
    })
}

export const useUpdateProduct = (id: number) => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (data: Partial<Product>) => productsApi.updateProduct(id, data), 
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: productKeys.all })
            toast.success('Product updated successfully')
        }, 
        onError: () => {
            toast.error('Failed to update product')
        }
    })
}

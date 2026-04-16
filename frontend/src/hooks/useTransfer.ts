import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { transferApi } from "@/api/transfer.api";
import toast from 'react-hot-toast'

export const transferKeys = {
    all: ['transfers'] as const, 
    list: (filters?: Record<string, unknown>) => 
        [...transferKeys.all, 'list', filters] as const, 
    detail: (id: number) => 
    [...transferKeys.all, 'detail', id] as const, 
}

export const useTransfers = (filters?: Record<string, unknown>) => 
    useQuery({
        queryKey: transferKeys.list(filters), 
        queryFn: () => transferApi.getTransfers(filters), 
    })

export const useApproveTransfer = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (id: number) => transferApi.approve(id), 
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: transferKeys.all})
            toast.success('Transfer approved')
        }
    })   
}

export const useDispatchTransfer = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (id: number) => transferApi.dispatch(id), 
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: transferKeys.all})
            toast.success('Transfer dispatched  - Stock deducted from source')
        }, 
        onError: (error: any) => {
            toast.error(error.response?.data?.message ?? 'Dispatch failed')
        },
    })
}
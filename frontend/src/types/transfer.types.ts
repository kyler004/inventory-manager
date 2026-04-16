export type TransferStatus = 
    | 'requested'
    | 'approved'
    | 'in_transit'
    | 'completed'
    | 'cancelled'

export interface TransferItem {
    id: number
    product: number
    product_name: number 
    batch: number | null
    batch_number: string | null
    quantity_requested: number 
    quantity_sent: number 
    quantity_received: number 
}

export interface StockTransfer {
    id: number 
    from_location: number 
    from_location_name: string
    to_location: number 
    to_location_name: string
    status: TransferStatus
    requested_by: number 
    requested_by_name: string
    approved_by: number | null
    notes: string
    items: TransferItem[]
    created_at: string
    completed_at: string | null
}
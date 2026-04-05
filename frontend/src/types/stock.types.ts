export type StockStatus = 'OK' | 'LOW' | 'OUT'

export interface StockLevel {
    id: number
    product: {
        id: number
        name: string
        sku: string
        unit_of_measure: string
    }
    location: number 
    location_name: string
    quantity_on_hand: number
    quantity_reserved: number 
    reorder_point: number 
    reorder_quantity: number
    stock_status: StockStatus
    last_updated: string
}

export interface StockMovement {
    id: number 
    product: number 
    product_name: string
    from_location: number | null
    to_location: number | null
    quantity: number 
    movement_type: string
    reference_id: string
    performed_by_name: string
    notes: string
    created_at: string
}

export interface StockAdjustment {
    product_id: number
    location_id: number
    quantity_after: number 
    reason: string
    notes?: string
}
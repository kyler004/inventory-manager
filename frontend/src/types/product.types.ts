export interface Category {
    id: number
    name: string
    parent: number | null
    subcategories: Category[]
}

export interface Product {
    id: number 
    name: string
    sku: string
    barcode: string | null
    category: number
    category_name: string
    brand: string
    unit_of_measure: string
    unit_price_cost: number 
    unit_price_retail: number
    tax_rate: number 
    margin: number 
    is_active: boolean
    created_at: string
    updated_at: string
}
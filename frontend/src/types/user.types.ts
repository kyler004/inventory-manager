export type UserRole = 
| 'Admin'
| 'WarehouseManager'
| 'StoreManager'
| 'Cashier'
| 'Auditor'

export interface User {
    id: number
    name: string
    email: string
    role: UserRole | null
    location_id: number | null
}

export interface AuthTokens {
    access: string
    refresh: string
}

export interface LoginResponse {
    access: string
    refresh: string
    user: User
}
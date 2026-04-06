import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

interface props {
    children: React.ReactNode
}

export const ProtectedRoute = ({ children }: props) => {
    const isAuthentcated = useAuthStore(state => state.isAuthenticated)
    
    if (!isAuthentcated) {
        // Redirect to login, preserving intended destination
        return <Navigate to='/login' replace/>
    }

    return <>{children}</>
}
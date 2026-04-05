import axios, { AxiosError, InternalAxiosRequestConfig} from 'axios' // => mihght need to change this later on unless the security issue with axios is over
import {useAuthStore} from '@store/authStore' // => will be implemented later

const client = axios.create({
    baseURL: '/api/v1', //Uses Vite proxy in dev, nginx will be used in production
    headers: {
        'Content-Type': 'application/json', 
    }, 
})

// Request interceptor
//Attaches the access token to every outgoing request 
client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = useAuthStore.getState().accessToken
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    }
)

// Request interceptor
//Automaticaly refreshes the access token when it expires

let isRefreshing = false 
let failedQueue: Array<{
    resolve: (token: string) => void
    reject: (error: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
    failedQueue.forEach(promise => {
        if (error) promise.reject(error)
            else promise.resolve(token!)
    })
    failedQueue = []
}

client.interceptors.response.use(
    response => response, 
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
            _retry?: boolean
        }

        if (error.response?.status === 401 && !originalRequest._retry) {
            // If already refreshing, queue this request
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({resolve, reject})
                }).then(token => {
                    originalRequest.headers.Authorization = `Bearer ${token}`
                    return client(originalRequest)
                })
            }

            originalRequest._retry = true
            isRefreshing = true

            const refreshToken = useAuthStore.getState().refreshToken

            try {
                const response = await axios.post('/api/v1/auth/token/refresh/', {
                    refresh: refreshToken, 
                })

                const newAccessToken = response.data.access
                useAuthStore.getState().setAccessToken(newAccessToken)
                processQueue(null, newAccessToken)

                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
                return client(originalRequest)
            } catch(refreshError) {
                // Refresh token also expired - force logout
                processQueue(refreshError, null)
                useAuthStore.getState().logout()
                window.location.href = '/login'
                return Promise.reject(refreshError)
            } finally {
                isRefreshing = false
            }
        }
        return Promise.reject(error)
    }
)

export default client
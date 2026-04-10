import { useAuthStore } from '@/store/authStore'
import { useAlertStore } from '@/store/alertStore'

class WebsocketManager {
    private socket: WebSocket | null = null
    private reconnectionTimeout: ReturnType<typeof setTimeout> | null = null
    private reconnectDelay = 3000 // Reconnect after 3 seconds

    connect() {
        const token = useAuthStore.getState().accessToken
        if (!token) return

        const wsUrl = `ws://localhost:8000/ws/alerts/?token=${token}`
        this.socket = new WebSocket(wsUrl)

        this.socket.onopen = () => {
            console.log('Websocket connected')
            //Clear any pending reconnect
            if (this.reconnectionTimeout) {
                clearTimeout(this.reconnectionTimeout)
                this.reconnectionTimeout = null
            }
        }

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data)
            const { addAlert, setInitialAlerts } = useAlertStore.getState()

            if (data.type === 'initial_alerts') {
                // Received on connect - populate existing alerts
                setInitialAlerts(data.alerts)
            } else if (data.type === 'send_alert') {
                // New alert pushed by the server
                addAlert(data)
            }
        }

        this.socket.onclose = () => {
            console.log('Webwocket disconnected - reconnecting...')
            // Auto-reconnect unless user logged out
            if (useAuthStore.getState().isAuthenticated) {
                this.reconnectionTimeout = setTimeout(
                    () => this.connect(), 
                    this.reconnectDelay
                )
            }
        }

        this.socket.onerror = (error) => {
            console.error('Websocket error:', error)
        }
    }

    disconnect() {
        if (this.reconnectionTimeout) {
            clearTimeout(this.reconnectionTimeout)
        }
        this.socket?.close()
        this.socket = null
    }

    resolveAlert(alertId: number) {
        this.socket?.send(JSON.stringify({
            type: 'resolve_alert', 
            alert_id: alertId, 
        }))
    }
}

// singleton - one websocket connection for the whole app
export const wsManager = new WebsocketManager()
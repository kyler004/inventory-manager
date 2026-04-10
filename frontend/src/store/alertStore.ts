import { create } from "zustand";

export interface AlertItem {
  id: number;
  alert_type: string;
  message: string;
  entity_type: string;
  created_at: string;
  is_read: boolean;
}

interface AlertState {
  alerts: AlertItem[];
  unreadCount: number;

  // Actions
  addAlert: (alert: AlertItem) => void;
  setInitialAlerts: (alerts: AlertItem[]) => void;
  markAsRead: (id: number) => void;
  markAllAsRead: () => void;
  resolveAlert: (id: number) => void;
}

export const useAlertStore = create<AlertState>((set, get) => ({
  alerts: [],
  unreadCount: 0,

  addAlert: (alert) =>
    set((state) => ({
      alerts: [{ ...alert, is_read: false }, ...state.alerts],
      unreadCount: state.unreadCount + 1,
    })),

  setInitialAlerts: (alerts) =>
    set({
      alerts: alerts.map(a => ({ ...a, is_read: true })),
      unreadCount: 0,
    }),

  markAsRead: (id) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === id ? { ...a, is_read: true } : a,
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),
  markAllAsRead: () =>
    set((state) => ({
      alerts: state.alerts.map((a) => ({ ...a, is_read: true })),
      unreadCount: 0,
    })),

  resolveAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
      unreadCount: state.alerts.find(
        (a => a.id === id && !a.is_read),
      )
        ? state.unreadCount - 1
        : state.unreadCount,
    })),
}));

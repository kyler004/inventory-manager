import { useAlertStore } from "@/store/alertStore";
import { wsManager } from "@/lib/websocket";
import { X, AlertTriangle, CheckCircle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

const alertColors: Record<string, string> = {
  low_stock: "text-yellow-600 bg-yellow-50",
  out_of_stock: "text-red-600 bg-red-50",
  near_expiry: "text-orange-600 bg-orange-50",
  expired: "text-red-600 bg-red-50",
  po_overdue: "text-purple-600 bg-purple-50",
};

interface Props {
  open: boolean;
  onClose: () => void;
}

export const AlertDrawer = ({ open, onClose }: Props) => {
  const { alerts, markAllAsRead, resolveAlert } = useAlertStore();

  const handleResolve = (id: number) => {
    wsManager.resolveAlert(id); // Tell the server
    resolveAlert(id); // Update local state
  };

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/20 z-40" onClick={onClose} />

      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-800">Alerts</h2>
          <div className="flex items-center gap-2">
            {alerts.some((a) => !a.is_read) && (
              <button
                onClick={markAllAsRead}
                className="text-xs text-blue-600 hover:underline"
              >
                Mark all read
              </button>
            )}
            <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Alert list */}
        <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
          {alerts.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <CheckCircle size={40} className="mb-3" />
              <p className="text-sm">All clear — no active alerts</p>
            </div>
          ) : (
            alerts.map((alert) => (
              <div
                key={alert.id}
                className={`px-6 py-4 ${!alert.is_read ? "bg-blue-50/50" : ""}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <span
                      className={`mt-0.5 p-1.5 rounded-lg text-xs font-medium ${alertColors[alert.alert_type] ?? "text-gray-600 bg-gray-50"}`}
                    >
                      <AlertTriangle size={14} />
                    </span>
                    <div>
                      <p className="text-sm text-gray-800">{alert.message}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatDistanceToNow(new Date(alert.created_at), {
                          addSuffix: true,
                        })}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleResolve(alert.id)}
                    className="text-xs text-gray-400 hover:text-green-600 shrink-0"
                  >
                    Resolve
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

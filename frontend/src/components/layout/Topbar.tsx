import { Bell, LogOut } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/api/auth.api";
import { useAlertStore } from "@/store/alertStore";
import { AlertDrawer } from "@/components/alerts/AlertDrawer";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { wsManager } from "@/lib/websocket";
import toast from "react-hot-toast";

export const Topbar = () => {
  const { user, refreshToken, logout } = useAuthStore();
  const navigate = useNavigate();

  const { unreadCount } = useAlertStore();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleLogout = async () => {
    wsManager.disconnect();
    try {
      if (refreshToken) await authApi.logout(refreshToken);
    } catch {
      // Logout locally event if API call fails
    } finally {
      logout();
      navigate("/login");
      toast.success("Logged out successfully");
    }
  };

  return (
    <header className="h-16 bg-xhite border-b border-gray-200 flex items-center justify-between px-6">
      <div />

      <div className="flex items-center gap-4">
        {/* Alert nell - wired to webscket*/}
        <button
          onClick={() => setDrawerOpen(true)}
          className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
        >
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </button>

        <AlertDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />

        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors "
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </header>
  );
};

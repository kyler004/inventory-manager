import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Package,
  Boxes,
  ShoppingCart,
  ArrowLeftRight,
  Users,
  BarChart2,
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import type { UserRole } from "@/types/user.types";

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  allowedRoles?: UserRole[];
}

const navItems: NavItem[] = [
  {
    label: "Dashboard",
    path: "/",
    icon: <LayoutDashboard size={18} />,
  },
  {
    label: "Products",
    path: "/products",
    icon: <Package size={18} />,
  },
  {
    label: "Stock",
    path: "/stock",
    icon: <Boxes size={18} />,
  },
  {
    label: "Purchase Orders",
    path: "/purchase-orders",
    icon: <ShoppingCart size={18} />,
    allowedRoles: ["Admin", "WarehouseManager"],
  },
  {
    label: "Transfers",
    path: "/transfers",
    icon: <ArrowLeftRight size={18} />,
  },
  {
    label: "Reports",
    path: "/reports",
    icon: <BarChart2 size={18} />,
    allowedRoles: ["Admin", "WarehouseManager", "StoreManager", "Auditor"],
  },
  {
    label: "Users",
    path: "/settings/users",
    icon: <Users size={18} />,
    allowedRoles: ["Admin"],
  },
];

export const Sidebar = () => {
  const user = useAuthStore((state) => state.user);

  const visibleItems = navItems.filter(
    (item) =>
      // Filter content accordint to user rolesin the allowed list from the navItems
      !item.allowedRoles ||
      (user?.role && item.allowedRoles.includes(user.role)),
  );

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        {/* Might need to change this to a better logo when time allows it */}
        <span className="text-xl font-bold text-blue-600">Inventory</span>
        <span className="text-xl font-bold text-gray-800">Pro</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? "bg-blue-50 text-blue-60" : "text-gray-600 hover:bg-gray-100"}`
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* User info at the bottom */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-blue-600 text-sm font-bold">
              {user?.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-800 truncate">
              {user?.name}
            </p>
            <p className="text-xs text-gray-500 truncate">{user?.role}</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

import { createBrowserRouter } from "react-router-dom";
import { ProtectedRoute } from "./ProtectedRoute";
import { RoleGuard } from "./RoleGuard";
import { AppShell } from "@/components/layout/AppShell";

import { LoginPage } from "@/pages/auth/LoginPage";
import { DashboardPage } from "@/pages/dashboard/DashboardPage";
import { ProductsPage } from "@/pages/products/ProductsPage";
import { StockPage } from "@/pages/stock/StockPage";
import { UnauthorizedPage } from "@/pages/UnauthorizedPage";
import { PurchaseOrdersPage } from "@/pages/purchase_orders/PurchaseOrdersPage";
import { TransfersPage } from "@/pages/transfers /TransfersPage";
import { ReportsPage } from "@/pages/reports/ReportsPage";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "products", element: <ProductsPage /> },
      { path: "stock", element: <StockPage /> },
      {
        path: "settings/users",
        element: (
          <RoleGuard
            allowedRoles={[
              "Admin",
              "Auditor",
              "Cashier",
              "StoreManager",
              "WarehouseManager",
            ]}
          >
            <div className="">USers Page - coming soon</div>
          </RoleGuard>
        ),
      },
      {
        path: "purchase-orders",
        element: (
          <RoleGuard allowedRoles={["Admin", "WarehouseManager"]}>
            <PurchaseOrdersPage />
          </RoleGuard>
        ),
      },
      {
        path: "transfers",
        element: (
          <RoleGuard
            allowedRoles={["Admin", "WarehouseManager", "StoreManager"]}
          >
            <TransfersPage />
          </RoleGuard>
        ),
      },
      {
        path: "reports",
        element: (
          <RoleGuard
            allowedRoles={[
              "Admin",
              "WarehouseManager",
              "StoreManager",
              "Auditor",
            ]}
          >
            <ReportsPage />
          </RoleGuard>
        ),
      },
    ],
  },
  { path: "/unauthorized", element: <UnauthorizedPage /> },
]);

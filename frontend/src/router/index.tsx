import { createBrowserRouter } from "react-router-dom";
import { ProtectedRoute } from "./ProtectedRoute";
import { RoleGuard } from "./RoleGuard";
import { AppShell } from "@/components/layout/AppShell";

import { LoginPage } from "@/pages/auth/LoginPage";
import { DashboardPage } from "@/pages/dashboard/DashboardPage";
import { ProductPage } from "@/pages/products/ProductsPage";
import { StockPage } from "@/pages/stock/StockPage";
import { UnauthorizedPage } from "@/pages/UnauthorizedPage";

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
      { path: "products", element: <ProductPage /> },
      { path: "stock", element: <StockPage /> },
      {
        path: "settings/users",
        element: (
          <RoleGuard>
            <div className="">USers Page - coming soon</div>
          </RoleGuard>
        ),
      },
    ],
  },
  { path: "/unauthorized", element: <UnauthorizedPage /> },
]);

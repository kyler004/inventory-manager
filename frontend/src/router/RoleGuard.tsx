import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import type { UserRole } from "@/types/user.types";

interface Props {
  allowedRoles: UserRole[];
  children: React.ReactNode;
}

export const RoleGuard = ({ allowedRoles, children }: Props) => {
  const user = useAuthStore((state) => state.user);

  if (!user?.role || !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

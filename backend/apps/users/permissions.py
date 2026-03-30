from rest_framework.permissions import BasePermission
from .models import Role


class IsAdmin(BasePermission):
    """Only system administrators."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role and
            request.user.role.name == Role.ADMIN
        )


class IsWarehouseManagerOrAbove(BasePermission):
    """Warehouse managers and admins."""
    ALLOWED_ROLES = [Role.ADMIN, Role.WAREHOUSE_MANAGER]

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role and
            request.user.role.name in self.ALLOWED_ROLES
        )


class IsStoreManagerOrAbove(BasePermission):
    """Store managers, warehouse managers, and admins."""
    ALLOWED_ROLES = [Role.ADMIN, Role.WAREHOUSE_MANAGER, Role.STORE_MANAGER]

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role and
            request.user.role.name in self.ALLOWED_ROLES
        )


class IsSameLocationOrAdmin(BasePermission):
    """
    Object-level permission.
    A store manager can only modify stock at their own location.
    Admins can modify anywhere.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role.name == Role.ADMIN:
            return True
        # obj must have a location field for this to work
        return obj.location == request.user.location
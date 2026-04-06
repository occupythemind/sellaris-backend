from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsStaffOrReadOnly(BasePermission):
    """
    - Read (GET, HEAD, OPTIONS): allowed for anyone
    - Write (POST, PUT, PATCH, DELETE): only for admin/staff
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
    

class IsStaffUser(BasePermission):
    """Allow only staffs"""
    def has_permission(self, request, view):

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
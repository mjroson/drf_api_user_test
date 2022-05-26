from rest_framework import permissions


class AdminOrStaffPermission(permissions.BasePermission):
    message = 'You need be a staff user o administrator to have permission.'

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))


class DeleteUserPermission(AdminOrStaffPermission):

    def has_object_permission(self, request, view, obj):
        """
            Regular users are not allowed to use this endpoint
        """
        # Admins can delete any user.
        if request.user.is_superuser:
            return True

        # Staff users can delete any other non-staff user.
        if request.user.is_staff and not obj.is_staff and not obj.is_superuser:
            return True

        return False

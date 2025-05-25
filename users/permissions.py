from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):


    def has_permission(self, request, view):
        # Allow access only if user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.is_staff:
            return True

        return obj == request.user
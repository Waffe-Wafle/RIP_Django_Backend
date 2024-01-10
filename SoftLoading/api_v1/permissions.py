from rest_framework.permissions import BasePermission


class IsUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and not (request.user.is_staff or request.user.is_superuser))


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_superuser)




# class AllowedRequestor(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user.is_authenticated and )


# class IsOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return bool(obj.user == request.user)

#
# class IsUser(permissions.BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
#
#
# class IsManager(permissions.BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         return bool(request.user and request.is_authenticated and (user.is_staff or user.is_superuser))
#
#
# class IsAdmin(permissions.BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         return bool(user and user.is_authenticated and user.is_superuser)
#
#
# class IsOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return bool(obj.user == request.user)
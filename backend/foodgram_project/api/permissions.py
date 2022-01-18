from rest_framework.permissions import BasePermission, SAFE_METHODS

PERMISSION_MESSAGE = 'Изменение чужого контента запрещено!'


class IsAuthorOrAdminOrReadOnly(BasePermission):

    message = PERMISSION_MESSAGE

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or (user.is_authenticated
                and (user.is_superuser or user.is_staff))
            or obj.author == request.user
        )

from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .permissions import AdminOrStaffPermission, DeleteUserPermission
from .serializers import MinimalUserModelSerializer, UserModelSerializer


class UserModelViewSet(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserModelSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == 'create':
            permission_classes += [AdminOrStaffPermission]
        elif self.action == "destroy":
            permission_classes += [DeleteUserPermission]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return UserModelSerializer

        return MinimalUserModelSerializer

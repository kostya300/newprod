from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username' # Можно получать /api/users/kostya/

    # Только админ может удалять или менять других
    def get_permissions(self):
        from rest_framework.permissions import IsAdminUser, AllowAny
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return[permission() for permission in permission_classes]
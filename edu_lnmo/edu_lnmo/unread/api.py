from rest_framework import viewsets, serializers, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import UnreadObject


class UnreadObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnreadObject
        fields = '__all__'


class UnreadObjectViewSet(viewsets.ModelViewSet):
    queryset = UnreadObject.objects.all()
    serializer_class = UnreadObjectSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.AllowAny]

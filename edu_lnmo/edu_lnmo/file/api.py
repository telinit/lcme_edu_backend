from rest_framework import permissions, viewsets, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

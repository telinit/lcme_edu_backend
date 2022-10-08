from rest_framework import viewsets, serializers, permissions
from rest_framework.authentication import SessionAuthentication

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.AllowAny]

from rest_framework import viewsets, serializers, permissions

from .models import UnreadObject


class UnreadObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnreadObject
        fields = '__all__'


class UnreadObjectViewSet(viewsets.ModelViewSet):
    queryset = UnreadObject.objects.all()
    serializer_class = UnreadObjectSerializer
    permission_classes = [permissions.AllowAny]

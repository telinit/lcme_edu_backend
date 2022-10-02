from rest_framework import permissions, viewsets, serializers

from .models import Mark


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'


class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = [permissions.AllowAny]
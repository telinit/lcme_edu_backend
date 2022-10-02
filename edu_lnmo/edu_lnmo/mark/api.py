from rest_framework import permissions, viewsets, serializers

from .models import Mark, MarkActivity, MarkFinal


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'


class MarkActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkActivity
        fields = '__all__'


class MarkFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkFinal
        fields = '__all__'


class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = [permissions.AllowAny]


class MarkActivityViewSet(viewsets.ModelViewSet):
    queryset = MarkActivity.objects.all()
    serializer_class = MarkActivitySerializer
    permission_classes = [permissions.AllowAny]


class MarkFinalViewSet(viewsets.ModelViewSet):
    queryset = MarkFinal.objects.all()
    serializer_class = MarkFinalSerializer
    permission_classes = [permissions.AllowAny]
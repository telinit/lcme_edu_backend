from rest_framework import viewsets, serializers, permissions

from .models import Activity, ActivityArticle, ActivityTask, ActivityMedia, ActivityLink


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class ActivityArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityArticle
        fields = '__all__'


class ActivityTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTask
        fields = '__all__'


class ActivityLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLink
        fields = '__all__'


class ActivityMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityMedia
        fields = '__all__'


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.AllowAny]


class ActivityArticleViewSet(viewsets.ModelViewSet):
    queryset = ActivityArticle.objects.all()
    serializer_class = ActivityArticleSerializer
    permission_classes = [permissions.AllowAny]


class ActivityTaskViewSet(viewsets.ModelViewSet):
    queryset = ActivityTask.objects.all()
    serializer_class = ActivityTaskSerializer
    permission_classes = [permissions.AllowAny]


class ActivityLinkViewSet(viewsets.ModelViewSet):
    queryset = ActivityLink.objects.all()
    serializer_class = ActivityLinkSerializer
    permission_classes = [permissions.AllowAny]


class ActivityMediaViewSet(viewsets.ModelViewSet):
    queryset = ActivityMedia.objects.all()
    serializer_class = ActivityMediaSerializer
    permission_classes = [permissions.AllowAny]

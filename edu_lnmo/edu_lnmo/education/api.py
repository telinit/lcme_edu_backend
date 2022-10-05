from rest_framework import permissions, serializers, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Education, EducationSpecialization


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class EducationSpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationSpecialization
        fields = '__all__'


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]


class EducationSpecializationViewSet(viewsets.ModelViewSet):
    queryset = EducationSpecialization.objects.all()
    serializer_class = EducationSpecializationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

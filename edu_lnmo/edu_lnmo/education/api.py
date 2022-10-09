from rest_framework import permissions, serializers, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Education, EducationSpecialization
from ..util.rest import EduModelViewSet, EduModelSerializer


class EducationSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Education
        fields = '__all__'


class EducationSpecializationSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = EducationSpecialization
        fields = '__all__'


class EducationViewSet(EduModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []


class EducationSpecializationViewSet(EduModelViewSet):
    queryset = EducationSpecialization.objects.all()
    serializer_class = EducationSpecializationSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []

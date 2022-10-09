from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Course, CourseEnrollment
from ..util.rest import EduModelViewSet, EduModelSerializer


class CourseSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Course
        fields = '__all__'


class CourseEnrollmentSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = CourseEnrollment
        fields = '__all__'


class CourseViewSet(EduModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []


class CourseEnrollmentViewSet(EduModelViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []
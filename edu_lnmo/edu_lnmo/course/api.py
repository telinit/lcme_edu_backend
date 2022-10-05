from rest_framework import serializers, viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Course, CourseEnrollment


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = '__all__'


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]
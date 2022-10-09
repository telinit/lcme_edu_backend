from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Organization, Department
from ..util.rest import EduModelViewSet, EduModelSerializer


class OrganizationSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Organization
        fields = '__all__'


class DepartmentSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Department
        fields = '__all__'


class OrganizationViewSet(EduModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []


class DepartmentViewSet(EduModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []
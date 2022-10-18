from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet


def request_user_is_authenticated(request: Request):
    return request.user and \
           request.user.is_authenticated


def request_user_is_staff(request: Request):
    return request_user_is_authenticated(request) and \
           (request.user.is_staff or request.user.is_superuser)


class EduModelViewSet(ModelViewSet):
    pass


class EduModelSerializer(ModelSerializer):
    id = serializers.UUIDField(allow_null=False, read_only=True)

    class Meta:
        read_only_fields = ['id']


class EduModelReadSerializer(ModelSerializer):
    pass
    #id = serializers.UUIDField(allow_null=False)


class EduModelWriteSerializer(ModelSerializer):
    class Meta:
        exclude = ['id']

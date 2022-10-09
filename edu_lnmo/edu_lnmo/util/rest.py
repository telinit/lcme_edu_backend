from rest_framework.request import Request
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
    class Meta:
        read_only_fields = ['id']

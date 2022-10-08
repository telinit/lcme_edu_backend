import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, F
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST

from .models import User
from ..course.models import CourseEnrollment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #fields = '__all__'
        exclude = ['password', 'pw_enc']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = [SessionAuthentication]

    def get_permissions(self):
        if self.action in ["login"]:
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]

    def get_queryset(self):
        u: User = self.request.user
        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return User.objects.all()
        else:
            courses = CourseEnrollment.get_courses_of_teacher(u)
            students = CourseEnrollment.get_students_of_courses(courses)

            # Children
            u1 = u.children.all()

            # Self
            u2 = User.objects.filter(id=u.id)

            # Own students
            u3 = User.objects.filter(id__in=students)

            # News writers
            u4 = User.objects.filter(messages_sent__messagenews__isnull=False, messages_sent__sender__id=F('id'))

            return (u1 | u2 | u3 | u4).distinct()

    @swagger_auto_schema(request_body=LoginSerializer, responses={200: 'Login succeeded. Cookies with a session key are set.', HTTP_403_FORBIDDEN: 'Wrong credentials'})
    @action(methods=['POST'], detail=False)
    def login(self, request: Request):
        user = authenticate(username=request.data["username"], password=request.data["password"])
        if user is not None:
            login(request, user)
            return Response()
        else:
            return Response('Wrong credentials', status=HTTP_403_FORBIDDEN)

    @swagger_auto_schema(responses={200: 'Loged out successfully',
                                    HTTP_400_BAD_REQUEST: 'Not logged in'})
    @action(methods=['GET'], detail=False)
    def logout(self, request: Request):
        if request.user is not None:
            logout(request)
            return Response()
        else:
            return Response('Not logged in', status=HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=SetPasswordSerializer,
                         responses={200: 'The password is updated'})
    @action(methods=['POST'], detail=False)
    def set_password(self, request: Request):
        request.user.set_password(request.data["password"])
        request.user.save()
        return Response()

    @swagger_auto_schema(responses={200: UserSerializer})
    @action(methods=['GET'], detail=False)
    def self(self, request: Request):
        return Response(UserSerializer(request.user).data)

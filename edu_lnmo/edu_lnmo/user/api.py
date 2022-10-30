import re
import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db.migrations import serializer
from django.db.models import Q, F
from drf_yasg.utils import swagger_auto_schema
from jwt import PyJWT
from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, permission_classes
from rest_framework.fields import SerializerMethodField
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, \
    HTTP_406_NOT_ACCEPTABLE

from .models import User
from ..course.models import CourseEnrollment
from ..education.models import Education
from ..settings import EMAIL_JWT_SECRET
from ..util.email import EmailManager
from ..util.rest import request_user_is_staff, EduModelViewSet, EduModelSerializer
from ..util.string import email_ok


class UserShallowSerializer(EduModelSerializer):
    roles = SerializerMethodField(method_name="get_roles", read_only=True, help_text="List of user's roles. A set of: admin, staff, teacher, student, parent")
    current_class = SerializerMethodField(method_name="get_class", read_only=True, help_text="Student's current class. null if none.")

    def get_roles(self, obj, *args, **kwargs) -> list[str]:
        u: User = obj

        res = []

        if u.children.all().count() > 0:
            res += ["parent"]

        if u.enrollments.filter(role=CourseEnrollment.EnrollmentRole.student).count() > 0:
            res += ["student"]

        if u.enrollments.filter(role=CourseEnrollment.EnrollmentRole.teacher).count() > 0:
            res += ["teacher"]

        if u.is_staff:
            res += ["staff"]

        if u.is_superuser:
            res += ["admin"]

        return res

    def get_class(self, user):

        edu = Education.objects\
            .filter(student=user, finished__isnull=True)\
            .order_by('-started')\
            .last()

        if not edu:
            return None
        else:
            return edu.get_current_class()


    class Meta(EduModelSerializer.Meta):
        model = User
        # fields = '__all__'
        exclude = ['password', 'pw_enc']


class UserDeepSerializer(UserShallowSerializer):
    children = UserShallowSerializer(many=True)
    class Meta(UserShallowSerializer.Meta):
        depth = 1


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255)

class ResetPasswordRequestSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=255)

class ResetPasswordCompleteSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=255)

class SetEmailSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)

class TokenSerializer(serializers.Serializer):
    user = UserDeepSerializer()
    key = serializers.CharField(max_length=40)

    class Meta(EduModelSerializer.Meta):
        model = Token
        fields = "__all__"
        depth = 1


class UserViewSet(EduModelViewSet):
    class UserPermissions(BasePermission):

        def has_permission(self, request: Request, view: "UserViewSet"):
            if view.action in ["login", "reset_password_request", "reset_password_complete"]:
                return True
            elif view.action == "create":
                return request_user_is_staff(request)
            elif view.action in ["list", "logout", "self", "set_password", "get_deep"]:
                return request.user and request.user.is_authenticated
            else:
                return False

        def has_object_permission(self, request: Request, view: "UserViewSet", obj):
            if view.action in ["retrieve", "get-deep"]:
                return True
            elif view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return False

    serializer_class = UserShallowSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [UserPermissions]

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

    @swagger_auto_schema(responses={200: UserDeepSerializer()})
    @action(methods=['GET'], detail=True, url_path='deep')
    def get_deep(self, request: Request, pk, *args, **kwargs):
        obj = self.get_queryset().filter(id=pk)
        if not obj:
            return Response(status=HTTP_404_NOT_FOUND)
        else:
            obj = obj.get()
            ser = UserDeepSerializer(obj)
            return Response(ser.data)

    @swagger_auto_schema(request_body=LoginSerializer,
                         responses={200: TokenSerializer,
                                    HTTP_403_FORBIDDEN: 'Wrong credentials'})
    @action(methods=['POST'], detail=False)
    def login(self, request: Request):
        user = authenticate(username=request.data["username"], password=request.data["password"])
        if user is not None:
            login(request, user)
            Token.objects.filter(user=user).delete()
            new_token = Token.objects.create(user=user)
            return Response(TokenSerializer({"key": new_token.key, "user": new_token.user}).data)
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
        password_ = request.data["password"]
        if not password_ or len(password_) < 5:
            return Response('Password is not valid', status=HTTP_400_BAD_REQUEST)

        if email_ok(request.user.email):
            EmailManager.send_notification_on_password_change(request.user.first_name, request.user.email)

        request.user.set_password(password_)
        request.user.save()
        return Response()

    @swagger_auto_schema(request_body=SetEmailSerializer,
                         responses={200: 'The email address is updated'})
    @action(methods=['POST'], detail=False)
    def set_email(self, request: Request):
        email_new = str(request.data["email"]).strip()

        if not email_new or not email_ok(email_new):
            return Response('Email is not valid', status=HTTP_400_BAD_REQUEST)

        existing_users = User.objects.filter(Q(email__iexact=email_new), ~Q(id=request.user.id))

        if existing_users:
            return Response('Email address already in use', status=HTTP_409_CONFLICT)

        if email_ok(request.user.email):
            EmailManager.send_notification_on_email_change(request.user.first_name, request.user.email)

        request.user.email = email_new
        request.user.save()
        return Response()

    @swagger_auto_schema(request_body=ResetPasswordRequestSerializer,
                         responses={200: 'Request was successful'})
    @action(methods=['POST'], detail=False)
    def reset_password_request(self, request: Request):
        login_ = str(request.data["login"]).strip()
        user = User.objects.filter(Q(username=login_) | Q(email__iexact=login_))
        if not user or not email_ok(user[0].email):
            return Response('Not found', status=HTTP_404_NOT_FOUND)

        user = user[0]

        if email_ok(user.email):
            EmailManager.send_password_reset(user.id, user.first_name, user.email)

        return Response()

    @swagger_auto_schema(request_body=ResetPasswordCompleteSerializer,
                         responses={200: 'Request was successful'})
    @action(methods=['POST'], detail=False)
    def reset_password_complete(self, request: Request):
        token = str(request.data["token"]).strip()

        jwt = PyJWT()
        data = jwt.decode(token, EMAIL_JWT_SECRET, ['HS256'])
        if data:
            user = User.objects.filter(id=data['uid'])

            if user:
                user = user[0]
                if email_ok(user.email):
                    EmailManager.send_notification_on_password_change(request.user.first_name, request.user.email)

                user.set_password()
                user.save()
                return Response()

        return Response('', status=HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(responses={200: UserDeepSerializer})
    @action(methods=['GET'], detail=False)
    def self(self, request: Request):
        return Response(UserDeepSerializer(request.user).data)

import re
import uuid
from typing import Optional

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser, update_last_login
from django.db import transaction
from django.db.migrations import serializer
from django.db.models import Q, F
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from jwt import PyJWT
from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action, permission_classes
from rest_framework.fields import SerializerMethodField, CharField
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, \
    HTTP_406_NOT_ACCEPTABLE, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_410_GONE, HTTP_401_UNAUTHORIZED

from .auth import MultiTokenAuthentication
from .models import User, MultiToken
from ..course.models import CourseEnrollment
from ..education.api import EducationShallowSerializer, EducationDeepSerializer, EducationSpecializationSerializer
from ..education.models import Education, EducationSpecialization
from ..imports.courses import CoursesDataImporter
from ..imports.students import StudentsDataImporter, StudentsImportResult
from ..olympiad.api import OlympiadSerializer, OlympiadParticipationSerializer
from ..settings import EMAIL_JWT_SECRET
from ..util.email import EmailManager
from ..util.rest import request_user_is_staff, EduModelViewSet, EduModelSerializer, request_user_is_admin
from ..util.string import email_ok


class UserShallowSerializer(EduModelSerializer):

    roles = SerializerMethodField(method_name="get_roles", read_only=True, help_text="List of user's roles. A set of: admin, staff, teacher, student, parent")
    current_class = SerializerMethodField(method_name="get_class", read_only=True, help_text="Student's current class. null if none.")
    current_spec = SerializerMethodField(method_name="get_spec", read_only=True, help_text="Student's current education specialization. null if none.")

    @swagger_serializer_method(serializers.ListField(
        child=serializers.CharField()
    ))
    def get_roles(self, obj) -> list[str]:
        u: User = obj

        return u.roles

    @swagger_serializer_method(serializer_or_field=CharField)
    def get_class(self, user) -> Optional[str]:

        edus = [*filter(lambda edu: edu.finished == None, user.education.all())]
        edus.sort(key=lambda edu: edu.started)

        if not edus:
            return None
        else:
            return edus[0].get_current_class()

    @swagger_serializer_method(serializer_or_field=EducationSpecializationSerializer)
    def get_spec(self, user) -> Optional[EducationSpecializationSerializer]:

        edus = [*filter(lambda edu: edu.finished is None, user.education.all())]
        edus.sort(key=lambda edu: edu.started)

        if not edus:
            return None
        else:
            return EducationSpecializationSerializer(instance=edus[0].specialization).data

    class Meta(EduModelSerializer.Meta):
        model = User
        # fields = '__all__'
        exclude = ['password', 'pw_enc', 'user_permissions', 'groups']


class UserDeepSerializer(UserShallowSerializer):
    children = UserShallowSerializer(many=True)
    parents = UserShallowSerializer(many=True)
    education = EducationShallowSerializer(many=True)

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
        model = MultiToken
        fields = "__all__"
        depth = 1

class ImportStudentsCSVRequest(serializers.Serializer):
    data = serializers.CharField()

class ImportStudentsCSVResult(serializers.Serializer):
    data = serializers.ListField(child=serializers.ListField(child=serializers.CharField()))


class ImportTeachersCSVRequest(serializers.Serializer):
    data = serializers.CharField()

class ImportTeachersCSVResult(serializers.Serializer):
    data = serializers.ListField(child=serializers.ListField(child=serializers.CharField()))

class UserViewSet(EduModelViewSet):
    class UserPermissions(BasePermission):

        def has_permission(self, request: Request, view: "UserViewSet"):
            if view.action == "impersonate":
                return request.user and request.user.is_superuser
            elif view.action in ["set_password", "set_email"]:
                return True  # Permissions are checked inside those functions
            elif view.action in ["retrieve", "get-deep", "login", "reset_password_request", "reset_password_complete"]:
                return True
            elif view.action in ["create", "import_students_csv", "import_teachers_csv"]:
                return request_user_is_staff(request)
            elif view.action in ["list", "logout", "self", "get_deep"]:
                return request.user and request.user.is_authenticated
            else:
                return False

        def has_object_permission(self, request: Request, view: "UserViewSet", obj):
            if view.action in ["retrieve", "get-deep"]:
                return True
            elif view.action in ["set_password", "set_email"]:
                return str(obj.id) == str(request.user.id) or request_user_is_staff(request)
            elif view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return False

    serializer_class = UserShallowSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [UserPermissions]
    filterset_fields = ["first_name", "last_name", "middle_name",
                        "enrollments__course","enrollments__role","enrollments__finished_on"]
    search_fields = ["first_name", "last_name", "middle_name"]

    def get_queryset(self):
        u: User = self.request.user
        if isinstance(u, AnonymousUser):
            return None
        else:
            return User.objects.prefetch_related(
                'children',
                'parents',
                'enrollments',
                'education',
                'education__specialization',
                'education__specialization__department',
                'education__specialization__department__organization',
                # 'groups',
                # 'children__groups',
                # 'parents__groups',
            ).all()

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
            MultiToken.objects.filter(user=user).delete()
            new_token = MultiToken.objects.create(user=user)
            update_last_login(None, user, )
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
    @action(methods=['POST'], detail=True)
    def set_password(self, request: Request, pk):
        if not request_user_is_staff(request) and str(pk) != str(request.user.id):
            return Response(status=HTTP_403_FORBIDDEN)

        user = User.objects.filter(id=pk)
        if not user:
            return Response(status=HTTP_404_NOT_FOUND)

        user = user[0]

        password_ = request.data["password"]
        if not password_ or len(password_) < 5:
            return Response('Password is not valid', status=HTTP_400_BAD_REQUEST)

        if email_ok(user.email):
            EmailManager.send_notification_on_password_change(user.first_name, user.email, is_reset=False)

        user.set_password(password_)
        user.save()
        return Response()

    @swagger_auto_schema(request_body=SetEmailSerializer,
                         responses={200: 'The email address is updated'})
    @action(methods=['POST'], detail=True)
    def set_email(self, request: Request, pk):
        if not request_user_is_staff(request) and str(pk) != str(request.user.id):
            return Response(status=HTTP_403_FORBIDDEN)

        user = User.objects.filter(id=pk)
        if not user:
            return Response(status=HTTP_404_NOT_FOUND)

        user = user[0]

        email_new = str(request.data["email"]).strip()

        if not email_new or not email_ok(email_new):
            return Response('Email is not valid', status=HTTP_400_BAD_REQUEST)

        existing_users = User.objects.filter(Q(email__iexact=email_new), ~Q(id=user.id))

        if existing_users:
            return Response('Email address already in use', status=HTTP_409_CONFLICT)

        if email_ok(user.email):
            EmailManager.send_notification_on_email_change(user.first_name, user.email)

        user.email = email_new
        user.save()
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
        ser = ResetPasswordCompleteSerializer(data=request.data)

        if not ser.is_valid():
            return Response('', status=HTTP_400_BAD_REQUEST)

        token = str(ser.validated_data["token"]).strip()

        jwt = PyJWT()
        try:
            data = jwt.decode(token, EMAIL_JWT_SECRET, ['HS256'])
        except:
            return Response('Bad token', status=HTTP_401_UNAUTHORIZED)

        if data and 'uid' in data:
            user = User.objects.filter(id=data['uid'])

            if user:
                user = user[0]
                if email_ok(user.email):
                    EmailManager.send_notification_on_password_change(
                        user.first_name,
                        user.email,
                        is_reset=True
                    )

                user.set_password(ser.validated_data["password"])
                user.save()
                return Response()

        return Response('', status=HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: UserDeepSerializer})
    @action(methods=['GET'], detail=False)
    def self(self, request: Request):
        return Response(UserDeepSerializer(request.user).data)

    @swagger_auto_schema(responses={200: "OK"})
    @action(methods=['GET'], detail=True)
    def impersonate(self, request: Request, pk):
        if not request_user_is_admin(request):
            return Response(status=HTTP_403_FORBIDDEN)

        if not User.objects.filter(id=pk):
            return Response('Not found', status=HTTP_404_NOT_FOUND)

        if request.auth:
            request.auth.user_id = pk
            request.auth.save()

            return Response()
        else:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=ImportStudentsCSVRequest,
                         responses={200: ImportStudentsCSVResult})
    @action(methods=['POST'], detail=False)
    def import_students_csv(self, request: Request):
        if not request_user_is_staff(request):
            return Response(status=HTTP_403_FORBIDDEN)

        ser = ImportStudentsCSVRequest(data=request.data)

        if not ser.is_valid():
            return Response('Bad data', status=HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            results: StudentsImportResult = StudentsDataImporter().do_import(ser.validated_data["data"])

            return Response(data={"data": results.report_rows})

    @swagger_auto_schema(request_body=ImportTeachersCSVRequest,
                         responses={200: ImportTeachersCSVResult})
    @action(methods=['POST'], detail=False)
    def import_teachers_csv(self, request: Request):
        if not request_user_is_staff(request):
            return Response(status=HTTP_403_FORBIDDEN)

        ser = ImportTeachersCSVRequest(data=request.data)

        if not ser.is_valid():
            return Response('Bad data', status=HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            results: StudentsImportResult = CoursesDataImporter().do_import(ser.validated_data["data"])

            return Response(data={"data": results.report_rows})
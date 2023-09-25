import hashlib
import io
import pathlib
import re
import uuid
from typing import Optional

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.http import FileResponse
from drf_yasg.openapi import Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.fields import SerializerMethodField, IntegerField, FileField, ModelField, UUIDField, CharField
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, \
    ListModelMixin
from rest_framework.parsers import MultiPartParser, FileUploadParser, JSONParser
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.status import HTTP_409_CONFLICT, HTTP_413_REQUEST_ENTITY_TOO_LARGE, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import File
from .. import settings
from ..common.api import ErrorMessageSerializer
from ..settings import FILE_QUOTA_PER_ROLE
from ..user.auth import MultiTokenAuthentication
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated
from ..util.string import filename_ok
from ..util.upload_storage import UploadFileStorage


class FileQuotaSerializer(Serializer):
    used = IntegerField()
    total = IntegerField()


class FileSerializer(EduModelSerializer):

    download_url = SerializerMethodField("get_download_url", read_only=True)

    def get_download_url(self, file):
        return f"/api/file/{file.id}/{file.name}"

    class Meta(EduModelSerializer.Meta):
        model = File
        fields = '__all__'


class MakeDirSerializer(Serializer):
    name = CharField(required=True)
    parent = PrimaryKeyRelatedField(queryset=File.objects.all(), required=False)


class Utils:
    @staticmethod
    def get_user_file_quota(user: User) -> Optional[FileQuotaSerializer]:
        used = File.objects.filter(
            owner=user
        ).aggregate(Sum('size'))['size__sum'] or 0

        if user.file_quota is not None:
            total = user.file_quota
        else:
            q: int = 0
            for r in user.roles:
                if r in FILE_QUOTA_PER_ROLE:
                    q = max(q, FILE_QUOTA_PER_ROLE[r])
            total = q

        res = FileQuotaSerializer(data={
            "used": used,
            "total": total
        })

        if res.is_valid():
            return res
        else:
            return None


class FileUploadAPI(GenericViewSet):
    parser_classes = [MultiPartParser]
    authentication_classes = [MultiTokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]

    class InputSerializer(Serializer):
        file = FileField()
        parent_file_id = UUIDField(required=False)

    @swagger_auto_schema(
        responses={
            HTTP_201_CREATED: FileSerializer(),
            HTTP_413_REQUEST_ENTITY_TOO_LARGE: ErrorMessageSerializer(),
            HTTP_409_CONFLICT: ErrorMessageSerializer(),
            HTTP_400_BAD_REQUEST: ErrorMessageSerializer(),
            HTTP_403_FORBIDDEN: ErrorMessageSerializer(),
        },
        request_body=InputSerializer)
    @action(methods=['POST'], detail=False)
    def upload(self, request: Request):
        ser = self.InputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if not filename_ok(ser.validated_data["file"].name):
            res = ErrorMessageSerializer(data={
                "code": HTTP_400_BAD_REQUEST,
                "message": "Загружаемый файл имеет недопустимое имя."
            })

            if res.is_valid(raise_exception=True):
                return Response(data=res.validated_data, status=HTTP_400_BAD_REQUEST)

        try:
            parent: File = File.objects.get(
                id=ser.validated_data["parent_file_id"]
            )

            if not parent.owner == request.user:
                res = ErrorMessageSerializer(data={
                    "code": HTTP_403_FORBIDDEN,
                    "message": "Доступ к родительскому каталогу запрещен."
                })

                if res.is_valid(raise_exception=True):
                    return Response(data=res.validated_data, status=HTTP_403_FORBIDDEN)

            if not parent.mime_type == "inode/directory":
                res = ErrorMessageSerializer(data={
                    "code": HTTP_400_BAD_REQUEST,
                    "message": "Указанный родительский элемент не является каталогом."
                })

                if res.is_valid(raise_exception=True):
                    return Response(data=res.validated_data, status=HTTP_400_BAD_REQUEST)
        except:
            parent = None

        # process file
        file: UploadedFile = ser.validated_data['file']
        file.seek(0, io.SEEK_SET)

        existing = File.objects.filter(
            name=file.name,
            parent=parent
        )
        if existing:
            res = ErrorMessageSerializer(data={
                "code": HTTP_409_CONFLICT,
                "message": "Загружаемый файл конфликтует с уже существующим."
            })
            if res.is_valid(raise_exception=True):
                return Response(data=res.validated_data, status=HTTP_409_CONFLICT)

        if not request.user.is_staff:
            quota = Utils.get_user_file_quota(request.user)
            if int(quota.data["used"]) + file.size > int(quota.data["total"]):
                res = ErrorMessageSerializer(data={
                    "code": HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    "message": "Загружаемый файл слишком большой или ваша квота превышена."
                })
                if res.is_valid(raise_exception=True):
                    return Response(data=res.validated_data, status=HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        stor = UploadFileStorage(settings.MEDIA_ROOT)
        hash = stor.store(file)

        new = File.objects.create(
            name=file.name,
            hash=hash,
            size=file.size,
            mime_type=file.content_type,  # TODO: Evaluate the mime type by using 'magic' lib, don't trust the client
            owner=request.user,
            parent=parent
        )

        res = FileSerializer(instance=new)

        return Response(status=HTTP_201_CREATED, data=res.data)


class FileViewSet(RetrieveModelMixin,
                   UpdateModelMixin,
                   DestroyModelMixin,
                   ListModelMixin,
                   GenericViewSet):

    class FilePermissions(BasePermission):

        def has_permission(self, request: Request, view: "FileViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "FileViewSet", obj: File):
            if view.action in ["update", "partial_update"]:
                return obj.owner == request.user or request_user_is_staff(request)
            if view.action in ["destroy"]:
                return obj.owner == request.user or request_user_is_staff(request)
            elif view.action in ["retrieve", "download"]:
                return request_user_is_authenticated(request)
            else:
                return False

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return File.objects.all()
        else:
            users = User.objects.filter(id=u.id) | u.children.all()
            # users = [*users.all()]
            q0 = Q(owner=u)
            q1 = Q(messages__sender=u)
            q2 = Q(messages__messageprivate__receiver=u)
            q3 = Q(course_covers__enrollments__person__in=users)
            q4 = Q(course_logos__enrollments__person__in=users)
            q5 = Q(activities__course__enrollments__person__in=users)
            return File.objects.filter(q0 | q1 | q2 | q3 | q4 | q5)

    serializer_class = FileSerializer
    authentication_classes = [MultiTokenAuthentication, SessionAuthentication]
    permission_classes = [FilePermissions]
    filterset_fields = dict((k, ['exact', 'isnull']) for k in ['name', 'hash', 'size', 'mime_type', 'owner', 'parent'])

    @swagger_auto_schema(responses={HTTP_200_OK: FileQuotaSerializer()})
    @action(methods=['GET'], detail=False, url_path='quota')
    def quota(self, request: Request, *args, **kwargs) -> Response:
        res = Utils.get_user_file_quota(request.user)

        return Response(status=HTTP_200_OK, data=res.validated_data)

    @action(methods=['GET'], detail=True, url_path='(?P<filename>[^/.]+)', url_name="download")
    def download(self, request: Request, pk: str, *args, **kwargs):
        try:
            stor = UploadFileStorage(settings.MEDIA_ROOT)
            obj: File = File.objects.get(id=pk)
            p = stor.get_path(str(obj.hash))
            if p.exists():
                return FileResponse(open(p, "rb"), filename=obj.name, content_type=obj.mime_type)
        except Exception as e:
            return Response(status=HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            HTTP_201_CREATED: FileSerializer(),
            HTTP_409_CONFLICT: ErrorMessageSerializer(),
            HTTP_400_BAD_REQUEST: ErrorMessageSerializer(),
            HTTP_403_FORBIDDEN: ErrorMessageSerializer(),},
        request_body=MakeDirSerializer)
    @action(methods=['POST'], detail=False, url_path='mkdir')
    def mkdir(self, request: Request, *args, **kwargs) -> Response:
        ser = MakeDirSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if not filename_ok(ser.validated_data["name"]):
            res = ErrorMessageSerializer(data={
                "code": HTTP_400_BAD_REQUEST,
                "message": "Загружаемый файл имеет недопустимое имя."
            })

            if res.is_valid(raise_exception=True):
                return Response(data=res.validated_data, status=HTTP_400_BAD_REQUEST)

        parent = ser.validated_data["parent"] if "parent" in ser.validated_data else None

        if parent:
            p: File = ser.validated_data["parent"]

            if p.owner != request.user:
                res = ErrorMessageSerializer(data={
                    "code": HTTP_403_FORBIDDEN,
                    "message": "Нет прав на родительский каталог."
                })
                if res.is_valid(raise_exception=True):
                    return Response(data=res.validated_data, status=HTTP_403_FORBIDDEN)

            if p.mime_type != "inode/directory":
                res = ErrorMessageSerializer(data={
                    "code": HTTP_400_BAD_REQUEST,
                    "message": "Родитель не является каталогом."
                })
                if res.is_valid(raise_exception=True):
                    return Response(data=res.validated_data, status=HTTP_400_BAD_REQUEST)

        existing = File.objects.filter(
            name=ser.validated_data["name"],
            parent=parent,
            owner=request.user
        )

        if existing.count() > 0:
            res = ErrorMessageSerializer(data={
                "code": HTTP_409_CONFLICT,
                "message": "Файл или каталог с таким именем уже существует."
            })
            if res.is_valid(raise_exception=True):
                return Response(data=res.validated_data, status=HTTP_409_CONFLICT)

        new = File.objects.create(
            name = ser.validated_data["name"],
            parent = parent,
            owner = request.user,
            hash = str(uuid.uuid4()),  # For directories, we pick a random value for a hash
            size = 0,
            mime_type = "inode/directory"
        )

        ser = FileSerializer(instance=new)

        return Response(data=ser.data, status=HTTP_201_CREATED)

    def perform_destroy(self, file: File):
        if file.mime_type == "inode/directory":
            if file.children.count() > 0:
                raise Exception("Parent is not empty")
        else:
            same_files = File.objects.filter(hash=file.hash)
            if len(same_files) == 1:  # Remove the file from the disk if it's the last link to the file
                stor = UploadFileStorage(settings.MEDIA_ROOT)
                stor.delete(str(file.hash))

        file.delete()

    def update(self, request, *args, **kwargs):
        if "name" in request.data:
            new_name = request.data["name"]

            if filename_ok(new_name):
                instance = self.get_object()
                instance.name = new_name
                instance.save()

                serializer = self.get_serializer(instance)

                return Response(serializer.data)

            else:
                res = ErrorMessageSerializer(data={
                    "code": HTTP_400_BAD_REQUEST,
                    "message": "Загружаемый файл имеет недопустимое имя."
                })

                if res.is_valid(raise_exception=True):
                    return Response(data=res.validated_data, status=HTTP_400_BAD_REQUEST)
        else:
            res = ErrorMessageSerializer(data={
                "code": HTTP_400_BAD_REQUEST,
                "message": "Некорректно указано новое имя файла"
            })
            if res.is_valid(raise_exception=True):
                return Response(data=res.validated_data, status=HTTP_400_BAD_REQUEST)
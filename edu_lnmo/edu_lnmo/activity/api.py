import datetime
import pdb
from typing import List, Optional

import ninja
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from ninja import Router, ModelSchema, Schema

from .models import *
from ..course.models import Course
from ..file.api import FileIO
from ..user.models import User
from ..util import HttpJWTRequest

router = Router()


class ActivityIO(Schema):
    from ninja import Field

    type: str = Field()

    # Base

    id: int = Field(default=None, title="ID активности")
    course_id: int = Field(title="ID курса")
    title: str = Field(title="Название")
    is_hidden: bool = Field(title="Скрытая")
    is_markable: bool = Field(title="Оцениваемая")
    order: int = Field(title="Номер в списке")

    # Article
    body: str = None
    attachments: List[int] = None

    # Task
    due_date: datetime.datetime = None

    # Link
    link: str = None
    embed: bool = None

    # Media
    file: int = None

    # Group
    children: List["ActivityIO"] = None


ActivityIO.update_forward_refs()


@router.get('/by_course/{cid}', response={200: List[ActivityIO], 403: None, 404: None})
def list_by_course(request: HttpJWTRequest, cid: int):
    course: Course = get_object_or_404(Course, id=cid)

    if not (request.is_admin or course.user_has_permissions(request.user_id, True, False)):
        return HttpResponseForbidden()

    return [ActivityIO(type=act.__class__.__name__, **vars(act))
            for act in Activity.objects.filter(course_id=cid)]


@router.post('/', response={
    400: None,
    404: None,
    403: None,
    200: ActivityIO
})
def create_or_update(
        request: HttpJWTRequest,
        payload: ActivityIO,
):
    course: Course = get_object_or_404(Course, id=payload.course_id)

    if not (request.is_admin or course.user_has_permissions(request.user_id, False, True)):
        return HttpResponseForbidden()

    t_map: dict[str, type] = {
        "ActivityBasic": ActivityBasic,
        "ActivityArticle": ActivityArticle,
        "ActivityTask": ActivityTask,
        "ActivityLink": ActivityLink,
        "ActivityMedia": ActivityMedia,
        "ActivityGroup": ActivityGroup,
    }

    if payload.type not in t_map:
        return HttpResponseBadRequest()

    t: type = t_map[payload.type]

    act: Activity = t()
    act.id = payload.id
    if payload.id is None:
        act.course_id = payload.course_id
    else:
        act_ex = get_object_or_404(Activity, id=payload.id)
        if act_ex.course_id == payload.course_id:
            act.course_id = payload.course_id
        else:
            return HttpResponseBadRequest()
    act.title = payload.title
    act.is_hidden = payload.is_hidden
    act.is_markable = payload.is_markable
    act.order = payload.order

    if act is ActivityArticle or act is ActivityTask:
        act.body = payload.body
        act.attachments.set(payload.attachments)

    if act is ActivityTask:
        act.due_date = payload.due_date

    if act is ActivityLink:
        act.link = payload.link
        act.embed = payload.embed

    if act is ActivityMedia:
        act.file = payload.file

    if act is ActivityGroup:
        act.children.set(payload.children)

    act.save()

    return ActivityIO(type = payload.type, **act.__dict__)
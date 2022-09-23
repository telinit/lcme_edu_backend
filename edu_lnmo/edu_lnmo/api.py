from ninja import NinjaAPI
from ninja.security import HttpBearer

from .user.api import router as router_user
from .course.api import router as router_course
from .activity.api import router as router_activity
from .mark.api import router as router_mark
from .message.api import router as router_message


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token


api = NinjaAPI(auth=AuthBearer())

api.add_router("/user", router_user)
api.add_router("/course", router_course)
api.add_router("/activity", router_activity)
api.add_router("/mark", router_mark)
api.add_router("/message", router_message)
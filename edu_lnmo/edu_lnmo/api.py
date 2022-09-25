from jwt import decode
from ninja import NinjaAPI
from ninja.security import HttpBearer

from .settings import JWT_PUBLIC_KEY
from .user.api import router as router_user
from .course.api import router as router_course
from .activity.api import router as router_activity
from .mark.api import router as router_mark
from .message.api import router as router_message


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        jwt = decode(
            jwt = token,
            key = JWT_PUBLIC_KEY,
            algorithms=['RS512']
        )

        if "edu_admin" not in jwt:
            jwt["edu_admin"] = False

        if "sub" not in jwt:
            raise Exception("Unauthorized")

        request.jwt = jwt
        request.user_id = jwt["sub"]
        request.is_admin = jwt["edu_admin"]

        return jwt


api = NinjaAPI(auth=AuthBearer())

api.add_router("/user", router_user)
api.add_router("/course", router_course)
api.add_router("/activity", router_activity)
api.add_router("/mark", router_mark)
api.add_router("/message", router_message)
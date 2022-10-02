from rest_framework import routers

from .activity.api import ActivityViewSet
from .common.api import DepartmentViewSet, OrganizationViewSet
from .course.api import CourseViewSet, CourseEnrollmentViewSet
from .education.api import EducationSpecializationViewSet, EducationViewSet
from .file.api import FileViewSet
from .mark.api import MarkViewSet
from .message.api import MessageNewsViewSet, MessageViewSet, MessageTaskSubmissionViewSet, MessagePrivateViewSet
from .unread.api import UnreadObjectViewSet
from .user.api import UserViewSet


api = routers.DefaultRouter()


api.register(r'activity', ActivityViewSet)

api.register(r'course/enrollment', CourseEnrollmentViewSet)
api.register(r'course', CourseViewSet)

api.register(r'common/organisation', OrganizationViewSet)
api.register(r'common/department', DepartmentViewSet)

api.register(r'education/specialization', EducationSpecializationViewSet)
api.register(r'education', EducationViewSet)

api.register(r'file', FileViewSet)

api.register(r'mark', MarkViewSet)

api.register(r'message/private', MessagePrivateViewSet)
api.register(r'message/task', MessageTaskSubmissionViewSet)
api.register(r'message/news', MessageNewsViewSet)
api.register(r'message', MessageViewSet)

api.register(r'unread', UnreadObjectViewSet)

api.register(r'user', UserViewSet)
from rest_framework import routers

from .activity.api import ActivityViewSet
from .common.api import DepartmentViewSet, OrganizationViewSet
from .course.api import CourseViewSet, CourseEnrollmentViewSet
from .education.api import EducationSpecializationViewSet, EducationViewSet
from .file.api import FileViewSet
from .mark.api import MarkViewSet
from .message.api import MessageNewsViewSet, MessageViewSet, MessageTaskSubmissionViewSet, MessagePrivateViewSet
from .stats.api import StatsViewSet
from .unread.api import UnreadObjectViewSet
from .user.api import UserViewSet

api = routers.DefaultRouter()


api.register(r'activity', ActivityViewSet, basename="Activity")

api.register(r'course/enrollment', CourseEnrollmentViewSet, basename="CourseEnrollment")
api.register(r'course', CourseViewSet, basename="Course")

api.register(r'common/organisation', OrganizationViewSet, basename="Organization")
api.register(r'common/department', DepartmentViewSet, basename="Department")

api.register(r'education/specialization', EducationSpecializationViewSet, basename="EducationSpecialization")
api.register(r'education', EducationViewSet, basename="Education")

api.register(r'file', FileViewSet, basename="File")

api.register(r'mark', MarkViewSet, basename="Mark")

api.register(r'message/private', MessagePrivateViewSet, basename="MessagePrivate")
api.register(r'message/task', MessageTaskSubmissionViewSet, basename="MessageTaskSubmission")
api.register(r'message/news', MessageNewsViewSet, basename="MessageNews")
api.register(r'message', MessageViewSet, basename="Message")

api.register(r'unread', UnreadObjectViewSet, basename="UnreadObject")

api.register(r'user', UserViewSet, basename="User")

api.register(r'stats', StatsViewSet, basename="Stats")

from rest_framework import routers

from .activity.api import ActivityViewSet
from .captcha.api import CaptchaViewSet
from .common.api import DepartmentViewSet, OrganizationViewSet
from .course.api import CourseViewSet, CourseEnrollmentViewSet
from .education.api import EducationSpecializationViewSet, EducationViewSet

from .file.api import FileViewSet, FileUploadAPI
from .mark.api import MarkViewSet
from .message.api import MessageViewSet
from .olympiad.api import OlympiadViewSet, OlympiadParticipationViewSet
from .stats.api import StatsViewSet
from .unread.api import UnreadObjectViewSet
from .user.api import UserViewSet

api = routers.DefaultRouter()


api.register(r'activity', ActivityViewSet, basename="Activity")

api.register(r'course/enrollment', CourseEnrollmentViewSet, basename="CourseEnrollment")
api.register(r'course', CourseViewSet, basename="Course")

api.register(r'common/organization', OrganizationViewSet, basename="Organization")
api.register(r'common/department', DepartmentViewSet, basename="Department")

api.register(r'education/specialization', EducationSpecializationViewSet, basename="EducationSpecialization")
api.register(r'education', EducationViewSet, basename="Education")

api.register(r'olympiad/participation', OlympiadParticipationViewSet, basename="OlympiadParticipation")
api.register(r'olympiad', OlympiadViewSet, basename="Olympiad")

api.register(r'file', FileUploadAPI, basename="FileUpload")
api.register(r'file', FileViewSet, basename="File")

api.register(r'mark', MarkViewSet, basename="Mark")
api.register(r'message', MessageViewSet, basename="Message")
api.register(r'unread', UnreadObjectViewSet, basename="UnreadObject")
api.register(r'user', UserViewSet, basename="User")
api.register(r'stats', StatsViewSet, basename="Stats")
api.register(r'captcha', CaptchaViewSet, basename="CaptchaViewSet")

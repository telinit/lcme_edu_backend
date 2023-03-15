import datetime
import sys
import traceback

from django.core import mail
from django.core.mail import send_mail
import urllib.parse

from django.views.debug import ExceptionReporter
from jwt import PyJWT

from ..settings import EMAIL_JWT_SECRET


class EmailManager(object):

    @staticmethod
    def make_email(body):
        pass

    @staticmethod
    def send_password_reset(uid, user_first_name, recipient):
        jwt = PyJWT()
        token = jwt.encode({"uid": str(uid), "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=5)}, EMAIL_JWT_SECRET, 'HS256')
        link = f"https://edu.lnmo.ru/login/password_reset?token={token}"

        msg = f"""Здравствуйте, {user_first_name}.
        
Кто-то (возможно, вы) запросил сброс пароля на Образовательном Портале ЛНМО (https://edu.lnmo.ru). 

Для завершения процедуры смены пароля пройдите по данной ссылке: {link}"""

        html_msg = f"""Здравствуйте, {user_first_name}.<br><br>
Кто-то (возможно, вы) запросил сброс пароля на <a href="https://edu.lnmo.ru">Образовательном Портале</a> ЛНМО. Для завершения процедуры смены пароля пройдите по данной <a href="{link}">ссылке</a>"""

        send_mail("ЛНМО | Восстановление пароля", msg, "edu@lnmo.ru", [recipient], html_message=html_msg)





    @staticmethod
    def send_notification_on_password_change(user_first_name, recipient, is_reset):
        h = "Был успешно выполнен сброс вашего пароля" if is_reset else "Был успешно изменен ваш пароль"
        msg = f"""Здравствуйте, {user_first_name}.

{h} на Образовательном Портале ЛНМО (https://edu.lnmo.ru). 

Если это были не вы, то рекомендуем как можно быстрее воспользователься функцией восстановления пароля, 
а также изменить ваш email в настройках вашего профиля."""

        html_msg = f"""Здравствуйте, {user_first_name}.<br><br>
        
{h} на <a href="https://edu.lnmo.ru">Образовательном Портале</a> ЛНМО. <br><br>

Если это были не вы, то рекомендуем как можно быстрее воспользоваться функцией восстановления пароля, 
а также изменить ваш email в настройках вашего профиля."""

        send_mail("ЛНМО | Изменение пароля", msg, "edu@lnmo.ru", [recipient], html_message=html_msg)





    @staticmethod
    def send_notification_on_email_change(user_first_name, recipient):
        msg = f"""Здравствуйте, {user_first_name}.

Был успешно изменен адрес электронной почты, указанный в вашем профиле на Образовательном Портале ЛНМО (https://edu.lnmo.ru). 

Если это были не вы, то рекомендуем как можно быстрее изменить ваш email и пароль в настройках вашего профиля."""

        html_msg = f"""Здравствуйте, {user_first_name}.<br><br>

Был успешно изменен адрес электронной почты, указанный в вашем профиле на <a href="https://edu.lnmo.ru">Образовательном Портале</a> ЛНМО.<br><br>

Если это были не вы, то рекомендуем как можно быстрее изменить ваш email и пароль в настройках вашего профиля."""

        send_mail("ЛНМО | Изменение почты", msg, "edu@lnmo.ru", [recipient], html_message=html_msg)

    @staticmethod
    def send_manually_exception_email(request, e: BaseException):
        try:
            raise e
        except BaseException:
            exc_info = sys.exc_info()
            reporter = ExceptionReporter(request, is_email=True, *exc_info)

            subject = str(e).replace('\n', '\\n').replace('\r', '\\r')[:989]
            message = "%s\n\n%s" % (
                '\n'.join(traceback.format_exception(*exc_info)),
                reporter.get_traceback_text()
            )
            mail.mail_admins(
                subject, message, fail_silently=True,
                html_message=reporter.get_traceback_html()
            )
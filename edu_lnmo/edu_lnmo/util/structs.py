from django.http import HttpRequest


class HttpJWTRequest(HttpRequest):
    user_id: str = None
    is_admin: bool = False
    jwt: dict = None

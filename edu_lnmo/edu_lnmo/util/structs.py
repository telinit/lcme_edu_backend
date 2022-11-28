from django.http import HttpRequest


class HttpJWTRequest(HttpRequest):
    user_id: str = ""
    is_admin: bool = False
    jwt: dict = {}

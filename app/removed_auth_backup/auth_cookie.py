from itsdangerous import URLSafeSerializer
from fastapi import Request, Response
import os

SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-secret-change-me")
COOKIE_NAME = "recipe_session"

serializer = URLSafeSerializer(SECRET_KEY)

def set_login_cookie(response: Response, username: str):
    token = serializer.dumps({"username": username})
    response.set_cookie(COOKIE_NAME, token, httponly=True, max_age=60*60*24*7)  # 7 days

def clear_login_cookie(response: Response):
    response.delete_cookie(COOKIE_NAME)

def get_current_username(request: Request) -> str | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        data = serializer.loads(token)
        return data.get("username")
    except Exception:
        return None
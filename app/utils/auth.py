import uuid
from fastapi import Request, Response
from typing import Optional


def get_or_create_user_id(request: Request, response: Optional[Response] = None) -> str:
    """
    Отримує user_id з cookie або створює новий, якщо відсутній.
    """
    user_id = request.cookies.get("user_id")

    if not user_id:
        user_id = str(uuid.uuid4())
        if response:
            response.set_cookie(
                key="user_id",
                value=user_id,
                httponly=True,
                samesite="Lax",
                max_age=60 * 60 * 24 * 30,  # 30 днів
            )

    return user_id

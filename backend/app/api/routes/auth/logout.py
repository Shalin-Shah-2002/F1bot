from fastapi import APIRouter, Request, Response

from app.core.auth_cookies import clear_auth_cookies, enforce_csrf_protection, get_access_token_from_request
from app.core.config import get_settings

router = APIRouter()


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response) -> Response:
    if get_access_token_from_request(request) is not None:
        enforce_csrf_protection(request)

    clear_auth_cookies(response, settings=get_settings())
    response.status_code = 204
    return response

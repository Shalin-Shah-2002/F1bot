from app.controllers.auth_controller import AuthController
from app.core.supabase_client import get_supabase_client


def get_auth_controller() -> AuthController:
    return AuthController(client=get_supabase_client())

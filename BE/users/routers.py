from fastapi import APIRouter, Depends

from users import services
from users.model import User
from users.schema import SignupRequest, LoginRequest, ResetPasswordRequest, ChangePasswordRequest, UserResponse
from users.utils import get_current_user


router = APIRouter()


@router.post("/signup/")
def signup(user_data: SignupRequest):
    access_token = services.signup_user(user_data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email/")
def verify_email(token: str):
    user = services.verify_user(token)
    if user:
        return {"message": "Email verified! You can now login."}


@router.post("/login")
def login(request: LoginRequest) -> dict:
    access_token = services.login(request.email, request.password)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected/")
def protected(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        restaurant_id=current_user.restaurant_id,
        tier=current_user.tier,
        message_count=current_user.message_count,
        is_subscribed=current_user.is_subscribed,
    )


@router.get("/forget_password")
def forget_password(email: str):
    return services.forget_password(email)


@router.post("/reset_password/{token}")
def reset_password(request: ResetPasswordRequest, token: str):
    return services.reset_password(token, request.password)


@router.post("/change-password")
def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user)):
    """
    Change the password for the authenticated user
    """
    return services.change_password(current_user, request.old_password, request.new_password)

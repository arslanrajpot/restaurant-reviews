from users.schema import SignupRequest
from fastapi import HTTPException
from users import repository
from users.utils import (
    get_password_hash,
    create_access_token,
    send_verification_email,
    get_current_user,
    verify_password,
    send_reset_password_email,
)
from users.model import User


def signup_user(user_data: SignupRequest) -> User:
    existing_user = repository.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    existing_phone = repository.get_user_by_phone_number(user_data.phone_number)
    if existing_phone:
        raise HTTPException(status_code=400, detail="Duplicate phone number")

    password = get_password_hash(user_data.password)
    user_payload = user_data.dict()
    user_payload["password"] = password
    user = repository.create_user(user_payload)
    access_token = create_access_token(data={"sub": user.email})

    # send_verification_email(user.email, user.name, access_token)
    return access_token


def verify_user(token: str):
    user = get_current_user(token)

    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    user.is_verified = True
    user.is_active = True

    return repository.verify_user(user)


def login(email, password) -> str:
    user = repository.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found.")

    # if not user.is_verified:
    #     raise HTTPException(status_code=400, detail="User not verified.")
    #
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="User not active.")

    if user.is_deleted:
        raise HTTPException(status_code=400, detail="This user account is deleted.")

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=403,
            detail="Incorrect password",
            # headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email}
    )
    return access_token


def forget_password(email):
    user = repository.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found.")
    access_token = create_access_token(data={"sub": user.email})
    send_reset_password_email(user.email, user.name, access_token)

    return {"message": "please check your email"}


def reset_password(token, password):
    user = get_current_user(token, is_token=True)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    if verify_password(password, user.password):
        raise HTTPException(
            status_code=403,
            detail="New password cannot be the same as the old password",
            # headers={"WWW-Authenticate": "Bearer"},
        )
    password = get_password_hash(password)
    return repository.update_password(user, password)


def change_password(user, old_password, new_password):
    """
    Change a user's password after verifying the old password
    """
    if not verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Hash the new password
    hashed_password = get_password_hash(new_password)
    
    # Update the password
    return repository.update_password(user, hashed_password)

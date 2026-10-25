
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from config_project.config import settings
from users.repository import get_user_by_email
from config_project.information_gathering.utils import send_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
bearer_schema = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_current_user(token: str = Depends(bearer_schema), is_token: bool = False):
    try:
        if is_token:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        else:
            payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    # if not user.is_verified:
    #     raise HTTPException(status_code=400, detail="User not verified.")
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="User not active.")
    if user.is_deleted:
        raise HTTPException(status_code=400, detail="This user account is deleted.")

    return user


def send_verification_email(receiver_email, name, access_token):
    verification_link = f"{settings.BASE_URL}/verify-email?token={access_token}"

    subject = "Verify Email"
    message = f"""
    <html>
      <body>
        <p>Dear {name},</p>
        <p>Click the link to verify your email: {verification_link}</p>
        <p>For security reasons, please change your password after logging in.</p>
        <p>If you did not request this, please contact support immediately.</p>
        <p>Best regards,</p>
      </body>
    </html>
    """
    send_email(receiver_email, subject, message)


def send_reset_password_email(receiver_email, name, access_token):
    verification_link = f"{settings.BASE_URL}/reset_password?token={access_token}"

    subject = "Reset Password"
    message = f"""
    <html>
      <body>
        <p>Dear {name},</p>
        <p>Click the link to reset the password: {verification_link}</p>
        <p>For security reasons, please change your password after logging in.</p>
        <p>If you did not request this, please contact support immediately.</p>
        <p>Best regards,</p>
      </body>
    </html>
    """
    send_email(receiver_email, subject, message)

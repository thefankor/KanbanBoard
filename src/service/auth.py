from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.config import settings
from src.schemas import AuthResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)

    @staticmethod
    def create_tokens(data: dict) -> AuthResponse:
        """Создание access и refresh токенов"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = AuthService.create_token(
            data=data,
            expires_delta=access_token_expires,
            secret_key=settings.ACCESS_SECRET_KEY
        )

        refresh_token = AuthService.create_token(
            data=data,
            expires_delta=refresh_token_expires,
            secret_key=settings.REFRESH_SECRET_KEY
        )

        return AuthResponse(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def create_token(data: dict, expires_delta: timedelta, secret_key: str) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_token_payload(token: str, is_refresh: bool = False) -> dict:
        """Получение payload из токена"""
        try:
            secret_key = settings.REFRESH_SECRET_KEY if is_refresh else settings.SECRET_KEY
            return jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> AuthResponse:
        """Обновление access токена с помощью refresh токена"""
        try:
            payload = AuthService.get_token_payload(refresh_token, is_refresh=True)
            username: str = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return AuthService.create_tokens({"sub": username})
        except HTTPException:
            raise
        except Exception as e:
            print(f"Unexpected error during token refresh: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during token refresh"
            )

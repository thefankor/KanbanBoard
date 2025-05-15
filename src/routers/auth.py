from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.dao import UserDAO
from src.dependencies import get_current_user
from src.models import User
from src.schemas import AuthResponse, CreateUserRequest, CreateUserResponse, RefreshTokenRequest
from src.service.auth import AuthService, pwd_context, oauth2_scheme
from fastapi import status

router = APIRouter(tags=["Auth"])


@router.post("/register", summary="Register new user")
async def register_user(
    user: CreateUserRequest, db_user: UserDAO = Depends()
) -> CreateUserResponse:
    existing_user = await db_user.find_one_or_none(username=user.username)

    if existing_user:
        raise HTTPException(status_code=400, detail="User is already registered")
    user.password = AuthService.get_password_hash(user.password)
    user = await db_user.add(
        email=user.email,
        name=user.name,
        username=user.username,
        hashed_password=user.password,
    )

    return CreateUserResponse(
        name=user.name,
        email=user.email,
        username=user.username,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", summary="Login to account")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_user: UserDAO = Depends(),
) -> AuthResponse:

    user = await db_user.find_one_or_none(username=form_data.username)

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return AuthService.create_tokens({"sub": user.username})



@router.post("/refresh", summary="Refresh access token")
async def refresh_token_api(
    data: RefreshTokenRequest
) -> AuthResponse:
    return await AuthService.refresh_access_token(data.refresh_token)

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.dao import UserDAO
from src.schemas import AuthResponse, CreateUserRequest, CreateUserResponse
from src.service.auth import AuthService, pwd_context
from fastapi import status

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", summary="Register new user")
async def register_user(
    user: CreateUserRequest, db_user: UserDAO = Depends()
) -> CreateUserResponse:
    existing_user = await db_user.find_one_or_none(username=user.username)

    if existing_user:
        raise HTTPException(status_code=400, detail="User is already registered")
    user.password = AuthService.get_password_hash(user.password)
    user = await db_user.add(**user.model_dump())

    return CreateUserResponse(
        name=user.name,
        email=user.email,
        username=user.username,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", summary="Login to account")
async def login(
    username: str,
    password: str,
    db_user: UserDAO = Depends(),
) -> AuthResponse:

    user = await db_user.find_one_or_none(username=username)

    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return AuthService.create_tokens({"sub": user.username})


@router.post("/refresh", summary="Refresh access token")
async def refresh_token_api(
    refresh_token: str = Depends(oauth2_scheme)
) -> AuthResponse:

    return await AuthService.refresh_access_token(refresh_token)

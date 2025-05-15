from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

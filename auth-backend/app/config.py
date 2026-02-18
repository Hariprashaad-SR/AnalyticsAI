from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = ""
    algorithm:  str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7   

    google_client_id:     str = ""
    google_client_secret: str = ""
    google_redirect_uri:  str = "http://localhost:8001/api/auth/google/callback"

    frontend_origin: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra    = "ignore"


settings = Settings()

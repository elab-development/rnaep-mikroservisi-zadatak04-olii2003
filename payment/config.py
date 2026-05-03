from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    inventory_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()

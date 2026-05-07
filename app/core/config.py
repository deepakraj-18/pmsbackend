import logging
from typing import Optional, Union, List, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TechnoRUCS PMS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    UPLOAD_DIR: str = "uploads"
    DEFAULT_LANGUAGE: str = "English"
    
    AUTO_SEED: bool = True
    ENABLE_DB_CREATE: bool = True
    LOG_LEVEL: str = "INFO"

    DB_USER: str = Field(default="root")
    DB_PASSWORD: str = Field(default="")
    DB_SERVER: str = Field(default="localhost")
    DB_PORT: str = Field(default="3306")
    DB_NAME: str = Field(default="trucsProjects")
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 280
    DB_POOL_TIMEOUT: int = 20

    @property
    def DATABASE_URL(self) -> str:
        from urllib.parse import quote_plus
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{self.DB_USER}:{encoded_password}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        from urllib.parse import quote_plus
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"mysql+aiomysql://{self.DB_USER}:{encoded_password}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}"

    SECRET_KEY: str = Field(default="7f0ee1c5d225de46bf357e6a")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Roles & Profiles
    ROLE_SUPER_ADMIN: str = "Super Admin"
    ROLE_ADMIN: str = "Admin"
    ROLE_TEAM_LEAD: str = "Team Lead"
    ROLE_EMPLOYEE: str = "Employee"

    PROFILE_PROJECT_LEAD: str = "Project Lead"
    PROFILE_DEVELOPER: str = "Developer"
    PROFILE_MEMBER: str = "Member"

    BACKEND_CORS_ORIGINS: Union[list[str], str] = Field(default=["*"])
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CORS_EXPOSE_HEADERS: List[str] = ["Content-Disposition"]
    ALLOWED_HOSTS: Union[list[str], str] = Field(default=["*"])

    @field_validator("BACKEND_CORS_ORIGINS", "ALLOWED_HOSTS", "PROXY_TRUSTED_HOSTS", mode="before")
    @classmethod
    def assemble_list(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                try:
                    import json
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, list):
            return [str(i) for i in v]
        return v or []

    PROXY_TRUSTED_HOSTS: Union[list[str], str] = Field(default="127.0.0.1")

    GZIP_MINIMUM_SIZE: int = 1024
    APP_PORT: int = 8000

    MS_LOGIN_BASE_URL: str = "https://login.microsoftonline.com"
    MS_GRAPH_BASE_URL: str = "https://graph.microsoft.com"
    MS_AUTH_SCOPES: str = "openid profile email User.Read"

    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None

    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

try:
    settings = Settings()
except Exception as e:
    print(f"CRITICAL: Settings failed to load: {e}")
    settings = Settings(_env_file=None)

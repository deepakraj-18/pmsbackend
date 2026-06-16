import os
import logging
from typing import Optional, Union, List, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TechSpear PMS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    UPLOAD_DIR: str = "uploads"
    DEFAULT_LANGUAGE: str = "English"
    
    AUTO_SEED: bool = True
    ENABLE_DB_CREATE: bool = True
    LOG_LEVEL: str = "INFO"

    DB_USER: str = Field(default="sa")
    DB_PASSWORD: str = Field(default="")
    DB_SERVER: str = Field(default="localhost")
    # Leave DB_PORT empty to omit the port, e.g. for a named instance
    # ("HOST\\INSTANCE") or a local default instance reached over shared memory.
    DB_PORT: str = Field(default="1433")
    DB_NAME: str = Field(default="techspear")
    DB_DRIVER: str = Field(default="ODBC Driver 18 for SQL Server")
    # Use Windows / integrated authentication instead of a SQL login. When true,
    # DB_USER / DB_PASSWORD are ignored and Trusted_Connection=yes is sent.
    DB_TRUSTED_CONNECTION: bool = Field(default=False)
    # Encrypt the connection (Azure SQL requires it). TrustServerCertificate=yes
    # lets local/self-signed servers connect without installing the server cert.
    DB_ENCRYPT: bool = Field(default=True)
    DB_TRUST_SERVER_CERTIFICATE: bool = Field(default=True)
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 280
    DB_POOL_TIMEOUT: int = 20

    def _odbc_query(self) -> str:
        from urllib.parse import urlencode
        params = {
            "driver": self.DB_DRIVER,
            "Encrypt": "yes" if self.DB_ENCRYPT else "no",
            "TrustServerCertificate": "yes" if self.DB_TRUST_SERVER_CERTIFICATE else "no",
        }
        if self.DB_TRUSTED_CONNECTION:
            params["Trusted_Connection"] = "yes"
        return urlencode(params)

    def _host(self) -> str:
        # Append the port only when one is configured; a named instance or a
        # local default instance over shared memory must omit it.
        return f"{self.DB_SERVER}:{self.DB_PORT}" if self.DB_PORT else self.DB_SERVER

    def _credentials(self) -> str:
        from urllib.parse import quote_plus
        if self.DB_TRUSTED_CONNECTION:
            return ""  # integrated auth: no userinfo in the URL
        return f"{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}@"

    def _build_url(self, driver_scheme: str) -> str:
        return (
            f"{driver_scheme}://{self._credentials()}{self._host()}"
            f"/{self.DB_NAME}?{self._odbc_query()}"
        )

    @property
    def DATABASE_URL(self) -> str:
        return self._build_url("mssql+pyodbc")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self._build_url("mssql+aioodbc")

    SECRET_KEY: str = Field(default="7f0ee1c5d225de46bf357e6a")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

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
    APP_PORT: int = int(os.getenv("PORT", 8000))

    MS_LOGIN_BASE_URL: str = "https://login.microsoftonline.com"
    MS_GRAPH_BASE_URL: str = "https://graph.microsoft.com"
    MS_AUTH_SCOPES: str = "openid profile email User.Read"

    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None

    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

try:
    settings = Settings()
except Exception as e:
    print(f"CRITICAL: Settings failed to load: {e}")
    settings = Settings(_env_file=None)

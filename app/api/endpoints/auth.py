from __future__ import annotations

from logging import getLogger
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from httpx import Client, HTTPStatusError

from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_sync_db
from app.core.security import create_access_token, create_refresh_token, get_current_user
from app.models.user import User
from app.schemas.auth import MSCallbackRequest, TokenResponse, RefreshTokenRequest
from app.services.user_service import upsert_o365_user

router = APIRouter()
logger = getLogger(__name__)

def _build_token_response(user: User) -> TokenResponse:
    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    role_data = {"id": user.role.id, "name": user.role.name, "permissions": user.role.permissions} if user.role else None
    return TokenResponse(
        access_token  = access_token,
        refresh_token = refresh_token,
        token_type    = "bearer",
        user_id      = user.id,
        public_id    = user.public_id,
        email        = user.email,
        first_name   = user.first_name,
        last_name    = user.last_name,
        display_name = user.display_name,
        role         = role_data,
        is_external  = user.is_external,
        is_synced    = user.is_synced,
    )

@router.post("/redirect", response_model=TokenResponse)
def ms_callback(payload: MSCallbackRequest, db: Session = Depends(get_sync_db)):
    logger.info("[SSO] Starting Microsoft callback for redirect_uri: %s", payload.redirect_uri)
    
    if not all([settings.AZURE_TENANT_ID, settings.AZURE_CLIENT_ID, settings.AZURE_CLIENT_SECRET]):
        logger.error("[SSO] Configuration missing: TENANT_ID=%s, CLIENT_ID=%s", 
                     bool(settings.AZURE_TENANT_ID), bool(settings.AZURE_CLIENT_ID))
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Microsoft SSO is not configured on this server.",
        )

    token_url = f"{settings.MS_LOGIN_BASE_URL}/{settings.AZURE_TENANT_ID}/oauth2/v2.0/token"
    try:
        logger.info("[SSO] Exchanging code with Microsoft...")
        with Client() as client:
            resp = client.post(
                token_url,
                data={
                    "grant_type":    "authorization_code",
                    "code":          payload.code,
                    "redirect_uri":  payload.redirect_uri,
                    "client_id":     settings.AZURE_CLIENT_ID,
                    "client_secret": settings.AZURE_CLIENT_SECRET,
                    "scope":         settings.MS_AUTH_SCOPES,
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            ms_tokens = resp.json()
            logger.info("[SSO] Token exchange successful")
    except HTTPStatusError as exc:
        logger.error("[SSO] MS token exchange failed: %s", exc.response.text)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Microsoft rejected the authorization code.")
    except Exception as exc:
        logger.exception("[SSO] MS token exchange error")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to reach Microsoft.")

    try:
        logger.info("[SSO] Fetching user profile from Microsoft Graph...")
        with Client() as client:
            graph_resp = client.get(
                f"{settings.MS_GRAPH_BASE_URL}/v1.0/me",
                headers={"Authorization": f"Bearer {ms_tokens['access_token']}"},
                timeout=10.0,
            )
            graph_resp.raise_for_status()
            ms_user = graph_resp.json()
            logger.info("[SSO] Microsoft Graph fetch successful for: %s", ms_user.get("userPrincipalName"))
    except Exception as exc:
        logger.exception("[SSO] MS Graph fetch failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch profile from Microsoft.")

    try:
        logger.info("[SSO] Upserting user in local database...")
        user = upsert_o365_user(
            db           = db,
            o365_id      = ms_user.get("id"),
            email        = ms_user.get("mail") or ms_user.get("userPrincipalName"),
            first_name   = ms_user.get("givenName", ""),
            last_name    = ms_user.get("surname", ""),
            display_name = ms_user.get("displayName"),
        )
        logger.info("[SSO] User upsert successful: ID=%s", user.id)
    except Exception as exc:
        logger.exception("[SSO] Database upsert failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database synchronization failed.")

    if user.is_deleted or not user.is_active:
        logger.warning("[SSO] Login blocked for inactive user: %s", user.email)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    try:
        logger.info("[SSO] Building final token response...")
        return _build_token_response(user)
    except Exception as exc:
        logger.exception("[SSO] Failed to build token response")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate authentication token.")

@router.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id":           current_user.id,
        "public_id":    current_user.public_id,
        "email":        current_user.email,
        "first_name":   current_user.first_name,
        "last_name":    current_user.last_name,
        "display_name": current_user.display_name,
        "role":         {"id": current_user.role.id, "name": current_user.role.name, "permissions": current_user.role.permissions} if current_user.role else None,
        "is_external":  current_user.is_external,
        "is_synced":    current_user.is_synced,
    }
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_sync_db)):
    try:
        decoded = jwt.decode(payload.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
            
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or user.is_deleted or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
            
        return _build_token_response(user)
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

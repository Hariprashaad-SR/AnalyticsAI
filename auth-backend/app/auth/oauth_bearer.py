from fastapi import Depends, HTTPException, status, Security
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from app.auth.jwt_handler import verify_access_token
from app.auth.blacklist import is_token_blacklisted
from app.database import get_db
# from app.models import Role, RolePermission, Permission
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login")

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    jti = payload.get("jti")
    if await is_token_blacklisted(db, jti):
        raise HTTPException(status_code=403, detail="Token has been revoked")

    # user_role = payload.get("role")
    # role_result = await db.execute(select(Role).where(Role.role == user_role))
    # role = role_result.scalars().first()
    # if not role:
    #     raise HTTPException(status_code=404, detail=f"Role '{user_role}' not found")

    # permissions_query = await db.execute(
    #     select(Permission.permission_name)
    #     .join(RolePermission, RolePermission.permission_id == Permission.permission_id)
    #     .where(RolePermission.role_id == role.role_id)
    # )
    # permissions = permissions_query.scalars().all()

    # for scope in security_scopes.scopes:
    #     if scope not in permissions:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Access forbidden: insufficient privileges"
    #         )

    return payload

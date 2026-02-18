from sqlalchemy.ext.asyncio import AsyncSession
from app.models import RevokedToken
from datetime import datetime, timezone
from sqlalchemy import select


async def add_to_blacklist(db: AsyncSession, jti: str, expires_at: datetime):
    if isinstance(expires_at, int):
        expires_at = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    else:
        expires_at = expires_at

    revoked = RevokedToken(jti=jti, expires_at=expires_at)
    db.add(revoked)
    await db.commit()


async def is_token_blacklisted(db: AsyncSession, jti: str) -> bool:
    token = await db.execute(select(RevokedToken).where(RevokedToken.jti == jti))
    token = token.scalars().first()
    if token:
        if token.expires_at < datetime.utcnow():
            db.delete(token)
            await db.commit()
            return False
        return True
    return False


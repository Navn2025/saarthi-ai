from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.token import create_access_token
from fastapi import APIRouter, HTTPException, status
from app.schemas.refresh import RefreshRequest

router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"]
)
@router.post("/refresh")
def refresh_token(data: RefreshRequest):
    try:
        payload = jwt.decode(
            data.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Check token type
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Create new access token
        new_access_token = create_access_token(
            data={"sub": email}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

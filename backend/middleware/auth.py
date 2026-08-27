from fastapi import Header, HTTPException, status, Depends
from typing import Optional
from shared.utils.security import decode_access_token
from config.database import db_manager

async def get_current_farmer(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired or is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    farmer_id = payload["sub"]
    farmer = db_manager.farmers.find_one({"farmerId": farmer_id})
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Farmer account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    farmer["_id"] = str(farmer["_id"])
    farmer.pop("hashedPassword", None)
    return farmer

async def get_optional_farmer(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization:
        return None
    try:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            payload = decode_access_token(parts[1])
            if payload and "sub" in payload:
                farmer = db_manager.farmers.find_one({"farmerId": payload["sub"]})
                if farmer:
                    farmer["_id"] = str(farmer["_id"])
                    farmer.pop("hashedPassword", None)
                    return farmer
    except Exception:
        pass
    return None

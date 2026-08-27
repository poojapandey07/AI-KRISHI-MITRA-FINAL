import random
import string
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from config.settings import settings

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def generate_id(prefix: str, length: int = 5) -> str:
    digits = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}-{digits}"

def mask_account_number(account_no: str) -> str:
    cleaned = str(account_no).strip()
    if len(cleaned) <= 4:
        return cleaned
    last_four = cleaned[-4:]
    masked = "•" * (len(cleaned) - 4) + last_four
    # Format nicely in groups of 4 if standard 12-16 digits
    chunks = [masked[max(i - 4, 0):i] for i in range(len(masked), 0, -4)]
    chunks.reverse()
    return " ".join(chunks)

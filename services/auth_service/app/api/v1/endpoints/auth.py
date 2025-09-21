from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.core.security import create_access_token, verify_token
from app.schemas.token_schema import Token
from app.schemas.user_schema import UserPublic, UserCreate
from app.crud.crud_user import authenticate_user, get_user_by_email, create_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
):
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user_id = payload["sub"]
    # Fetch by id using proper UUID casting
    from sqlalchemy import select
    from app.models.user_model import User
    import uuid as _uuid

    try:
        user_uuid = _uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserPublic, status_code=201)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, payload)

    # Publish USER_CREATED event (best-effort)
    try:
        from app.core.messaging import publish_user_created
        await publish_user_created(user_id=str(user.id), user_email=user.email, workspace_name=payload.workspace_name)
    except Exception:
        # Don't block registration on messaging failures
        pass

    return user

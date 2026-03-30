from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import (
    UserLoginRequest,
    UserPasswordResetRequest,
    UserProfileUpdateRequest,
    UserPublicRead,
)
from app.services.user_service import UserService


router = APIRouter(prefix="/api/auth", tags=["auth"])



def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)



def require_current_user(request: Request, service: UserService = Depends(get_user_service)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或登录已失效")

    user = service.get_user_by_id(int(user_id))
    if not user or not user.is_active:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不可用，请重新登录")
    return user


@router.get("/me", response_model=UserPublicRead)
def get_current_user_profile(user=Depends(require_current_user), service: UserService = Depends(get_user_service)):
    return UserPublicRead(**service.to_public(user))


@router.post("/login", response_model=UserPublicRead)
def login(payload: UserLoginRequest, request: Request, service: UserService = Depends(get_user_service)):
    user = service.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    request.session["user_id"] = user.id
    return UserPublicRead(**service.to_public(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request):
    request.session.clear()
    return None


@router.put("/profile", response_model=UserPublicRead)
def update_profile(
    payload: UserProfileUpdateRequest,
    request: Request,
    user=Depends(require_current_user),
    service: UserService = Depends(get_user_service),
):
    try:
        updated = service.update_profile(user.id, payload.username, payload.display_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    request.session["user_id"] = updated.id
    return UserPublicRead(**service.to_public(updated))


@router.post("/password/reset", response_model=UserPublicRead)
def reset_password(
    payload: UserPasswordResetRequest,
    user=Depends(require_current_user),
    service: UserService = Depends(get_user_service),
):
    try:
        updated = service.reset_password(user.id, payload.old_password, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserPublicRead(**service.to_public(updated))

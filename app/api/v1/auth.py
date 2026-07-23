from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.audit_logs import get_audit_log_service
from app.core.deps import CurrentUser, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.audit_log import AuditAction
from app.models.user import Token, UserCreate, UserLogin, UserOut, UserRole
from app.repositories.user_repository import UserRepository
from app.services.audit_log_service import AuditLogService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_repository() -> UserRepository:
    return UserRepository()


def to_user_out(doc: dict) -> UserOut:
    return UserOut(id=str(doc["_id"]), full_name=doc["full_name"], email=doc["email"], role=UserRole(doc["role"]))


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    repo: UserRepository = Depends(get_user_repository),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    existing_user = await repo.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu e-posta zaten kayıtlı")

    user_doc = {
        "full_name": user_in.full_name,
        "email": user_in.email,
        "hashed_password": hash_password(user_in.password),
        "role": user_in.role.value,
    }
    inserted_id = await repo.create(user_doc)

    await audit_service.record(
        actor_user_id=str(inserted_id),
        actor_email=user_in.email,
        actor_role=user_in.role,
        action=AuditAction.USER_REGISTERED,
        description=f"Yeni kullanıcı kaydoldu: {user_in.email} ({user_in.role.value}).",
        entity_type="user",
        entity_id=str(inserted_id),
    )

    return UserOut(id=str(inserted_id), full_name=user_in.full_name, email=user_in.email, role=user_in.role)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    repo: UserRepository = Depends(get_user_repository),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    user = await repo.get_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-posta veya şifre hatalı")

    access_token = create_access_token(subject=str(user["_id"]), role=user["role"], email=user["email"])

    await audit_service.record(
        actor_user_id=str(user["_id"]),
        actor_email=user["email"],
        actor_role=UserRole(user["role"]),
        action=AuditAction.USER_LOGGED_IN,
        description=f"{user['email']} giriş yaptı.",
        entity_type="user",
        entity_id=str(user["_id"]),
    )

    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
async def read_current_user(
    current_user: CurrentUser = Depends(get_current_user),
    repo: UserRepository = Depends(get_user_repository),
):
    user = await repo.find_one({"_id": ObjectId(current_user.id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
    return to_user_out(user)

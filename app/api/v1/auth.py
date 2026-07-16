from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Token, UserCreate, UserLogin, UserOut, UserRole
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_repository() -> UserRepository:
    return UserRepository()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, repo: UserRepository = Depends(get_user_repository)):
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

    return UserOut(id=str(inserted_id), full_name=user_in.full_name, email=user_in.email, role=user_in.role)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, repo: UserRepository = Depends(get_user_repository)):
    user = await repo.get_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-posta veya şifre hatalı")

    access_token = create_access_token(subject=str(user["_id"]), role=user["role"])
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
async def read_current_user(
    current_user: CurrentUser = Depends(get_current_user),
    repo: UserRepository = Depends(get_user_repository),
):
    user = await repo.find_one({"_id": ObjectId(current_user.id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")
    return UserOut(id=str(user["_id"]), full_name=user["full_name"], email=user["email"], role=UserRole(user["role"]))

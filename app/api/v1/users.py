from fastapi import APIRouter, Depends

from app.api.v1.auth import get_user_repository, to_user_out
from app.core.deps import CurrentUser, require_role
from app.models.user import UserOut, UserRole
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/drivers", response_model=list[UserOut])
async def list_drivers(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    repo: UserRepository = Depends(get_user_repository),
):
    drivers = await repo.list_by_role(UserRole.DRIVER.value)
    return [to_user_out(driver) for driver in drivers]

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import JSONResponse

from app.api.v1.auth import get_user_repository
from app.api.v1.routes import get_route_service, to_route_out
from app.core.deps import CurrentUser, require_role
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.services.csv_route_import import CsvValidationError
from app.services.import_service import ImportService
from app.services.route_service import RouteService

router = APIRouter(prefix="/imports", tags=["imports"])


def get_import_service(
    route_service: RouteService = Depends(get_route_service),
    user_repo: UserRepository = Depends(get_user_repository),
) -> ImportService:
    return ImportService(route_service, user_repo)


@router.post("/routes/csv")
async def import_routes_csv(
    file: UploadFile = File(...),
    route_name: str = Form(...),
    vehicle_id: str = Form(...),
    expected_revenue: float = Form(...),
    distance_km: float = Form(...),
    assigned_driver_id: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: ImportService = Depends(get_import_service),
):
    csv_bytes = await file.read()

    try:
        route_doc = await service.import_routes_csv(
            csv_bytes=csv_bytes,
            route_name=route_name,
            vehicle_id=vehicle_id,
            expected_revenue=expected_revenue,
            distance_km=distance_km,
            assigned_driver_id=assigned_driver_id or None,
            created_by=current_user.id,
        )
    except CsvValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "CSV doğrulama hataları bulundu.", "errors": exc.errors},
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "CSV başarıyla içe aktarıldı.",
            "route": to_route_out(route_doc).model_dump(mode="json"),
        },
    )

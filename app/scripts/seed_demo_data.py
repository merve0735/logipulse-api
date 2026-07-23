"""
Demo veri oluşturma scripti.

Calistirma:
    docker compose exec api python -m app.scripts.seed_demo_data

Idempotent'tir: iki kez calistirilirsa mevcut kullanicilar (email ile),
araclar (plaka ile) ve rotalar (seed_name ile) tekrar olusturulmaz.
Mevcut veritabanini silmez, sadece eksik demo kayitlarini ekler.
"""

import asyncio
from datetime import datetime, timezone

from app.core.security import hash_password
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.models.audit_log import AuditAction
from app.models.route import RouteCreate
from app.models.stop import StopDeliverRequest
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.services.audit_log_service import AuditLogService
from app.services.route_service import RouteService
from app.services.stop_service import StopService

ADMIN_EMAIL = "admin@logipulse.demo"
DRIVER1_EMAIL = "driver1@logipulse.demo"
DRIVER2_EMAIL = "driver2@logipulse.demo"
DRIVER3_EMAIL = "driver3@logipulse.demo"


async def get_or_create_user(
    user_repo: UserRepository,
    email: str,
    full_name: str,
    password: str,
    role: str,
    last_location: dict | None = None,
) -> dict:
    existing = await user_repo.get_by_email(email)
    if existing:
        print(f"  kullanici zaten var, atlaniyor: {email}")
        return existing

    user_doc = {
        "full_name": full_name,
        "email": email,
        "hashed_password": hash_password(password),
        "role": role,
    }
    if last_location:
        user_doc["last_location"] = last_location

    inserted_id = await user_repo.create(user_doc)
    user_doc["_id"] = inserted_id
    print(f"  kullanici olusturuldu: {email}")
    return user_doc


async def get_or_create_vehicle(
    vehicle_repo: VehicleRepository,
    plate_number: str,
    vehicle_type: str,
    capacity_kg: float,
    average_cost_per_km: float,
    average_carbon_per_km: float,
    is_active: bool,
) -> dict:
    existing = await vehicle_repo.get_by_plate_number(plate_number)
    if existing:
        print(f"  arac zaten var, atlaniyor: {plate_number}")
        return existing

    vehicle_doc = {
        "plate_number": plate_number,
        "vehicle_type": vehicle_type,
        "capacity_kg": capacity_kg,
        "average_cost_per_km": average_cost_per_km,
        "average_carbon_per_km": average_carbon_per_km,
        "is_active": is_active,
        "created_at": datetime.now(timezone.utc),
    }
    inserted_id = await vehicle_repo.create(vehicle_doc)
    vehicle_doc["_id"] = inserted_id
    print(f"  arac olusturuldu: {plate_number}")
    return vehicle_doc


async def route_exists(route_repo: RouteRepository, seed_name: str) -> bool:
    existing = await route_repo.collection.find_one({"seed_name": seed_name})
    return existing is not None


async def tag_route_with_seed_name(route_repo: RouteRepository, route_object_id, seed_name: str) -> None:
    await route_repo.update_one({"_id": route_object_id}, {"seed_name": seed_name})


async def seed_users(user_repo: UserRepository) -> dict:
    admin = await get_or_create_user(user_repo, ADMIN_EMAIL, "LogiPulse Demo Admin", "Admin12345", "admin")
    driver1 = await get_or_create_user(
        user_repo,
        DRIVER1_EMAIL,
        "Demo Driver 1",
        "Driver12345",
        "driver",
        last_location={"latitude": 36.8841, "longitude": 30.7056, "updated_at": datetime.now(timezone.utc)},
    )
    driver2 = await get_or_create_user(
        user_repo,
        DRIVER2_EMAIL,
        "Demo Driver 2",
        "Driver12345",
        "driver",
        last_location={"latitude": 36.8870, "longitude": 30.7075, "updated_at": datetime.now(timezone.utc)},
    )
    driver3 = await get_or_create_user(user_repo, DRIVER3_EMAIL, "Demo Driver 3", "Driver12345", "driver")
    return {"admin": admin, "driver1": driver1, "driver2": driver2, "driver3": driver3}


async def seed_vehicles(vehicle_repo: VehicleRepository) -> dict:
    electric_van = await get_or_create_vehicle(vehicle_repo, "07 EV 001", "electric_van", 500, 4, 0.05, True)
    diesel_van = await get_or_create_vehicle(vehicle_repo, "07 DSL 001", "diesel_van", 800, 9, 0.45, True)
    motorcycle = await get_or_create_vehicle(vehicle_repo, "07 MTR 001", "motorcycle", 50, 3, 0.12, True)
    await get_or_create_vehicle(vehicle_repo, "07 OLD 001", "diesel_van", 600, 12, 0.55, False)
    return {"electric_van": electric_van, "diesel_van": diesel_van, "motorcycle": motorcycle}


async def seed_routes(
    route_repo: RouteRepository,
    route_service: RouteService,
    stop_service: StopService,
    users: dict,
    vehicles: dict,
) -> None:
    admin_id = str(users["admin"]["_id"])
    driver1_id = str(users["driver1"]["_id"])
    driver2_id = str(users["driver2"]["_id"])
    ev_id = str(vehicles["electric_van"]["_id"])
    diesel_id = str(vehicles["diesel_van"]["_id"])
    moto_id = str(vehicles["motorcycle"]["_id"])

    # Rota 1: Karli elektrikli teslimat - in_progress, 1 delivered + 2 pending stop
    name = "Konyaalti Elektrikli Teslimat Rotasi"
    if await route_exists(route_repo, name):
        print(f"  rota zaten var, atlaniyor: {name}")
    else:
        route = await route_service.create_route(
            RouteCreate(
                origin="Konyaalti Depo",
                destination="Konyaalti Sahil",
                distance_km=32,
                vehicle_id=ev_id,
                expected_revenue=950,
                assigned_driver_id=driver1_id,
                stops=[
                    {"sequence_number": 1, "customer_name": "Ayse Yilmaz", "address": "Konyaalti Sahil Cad. No:12"},
                    {"sequence_number": 2, "customer_name": "Mehmet Demir", "address": "Konyaalti Liman Mah. No:5"},
                    {"sequence_number": 3, "customer_name": "Zeynep Kaya", "address": "Konyaalti Akdeniz Mah. No:8"},
                ],
            ),
            created_by=admin_id,
        )
        route_id = str(route["_id"])
        await tag_route_with_seed_name(route_repo, route["_id"], name)
        await route_service.assign_driver(route_id, driver1_id)
        route = await route_service.start_route(route_id, driver1_id)
        await stop_service.deliver_stop(
            route_id,
            route["stops"][0]["id"],
            driver1_id,
            StopDeliverRequest(recipient_name="Ayse Yilmaz", delivery_note="Kapida teslim edildi."),
        )
        print(f"  rota olusturuldu: {name}")

    # Rota 2: Zarar eden dizel rota - assigned, 1 failed + 1 retry_scheduled stop
    name = "Muratpasa Zarar Eden Dizel Rota"
    if await route_exists(route_repo, name):
        print(f"  rota zaten var, atlaniyor: {name}")
    else:
        route = await route_service.create_route(
            RouteCreate(
                origin="Muratpasa Depo",
                destination="Muratpasa Merkez",
                distance_km=80,
                vehicle_id=diesel_id,
                expected_revenue=500,
                assigned_driver_id=driver2_id,
                stops=[
                    {"sequence_number": 1, "customer_name": "Ali Veli", "address": "Muratpasa Fener Mah. No:3"},
                    {"sequence_number": 2, "customer_name": "Fatma Sahin", "address": "Muratpasa Meltem Mah. No:9"},
                ],
            ),
            created_by=admin_id,
        )
        route_id = str(route["_id"])
        await tag_route_with_seed_name(route_repo, route["_id"], name)
        route = await route_service.assign_driver(route_id, driver2_id)
        await stop_service.fail_stop(route_id, route["stops"][0]["id"], driver2_id, "Musteri adreste bulunamadi")
        await stop_service.schedule_retry_stop(route_id, route["stops"][1]["id"], driver2_id)
        print(f"  rota olusturuldu: {name}")

    # Rota 3: Yuksek karbonlu uzun dizel rota - in_progress, 1 skipped + 2 pending stop
    name = "Antalya Uzun Mesafe Dizel Rota"
    if await route_exists(route_repo, name):
        print(f"  rota zaten var, atlaniyor: {name}")
    else:
        route = await route_service.create_route(
            RouteCreate(
                origin="Antalya Depo",
                destination="Alanya",
                distance_km=150,
                vehicle_id=diesel_id,
                expected_revenue=2500,
                assigned_driver_id=driver2_id,
                stops=[
                    {"sequence_number": 1, "customer_name": "Can Ozturk", "address": "Alanya Merkez No:1"},
                    {"sequence_number": 2, "customer_name": "Elif Arslan", "address": "Alanya Oba Mah. No:4"},
                    {"sequence_number": 3, "customer_name": "Burak Kilic", "address": "Alanya Mahmutlar No:7"},
                ],
            ),
            created_by=admin_id,
        )
        route_id = str(route["_id"])
        await tag_route_with_seed_name(route_repo, route["_id"], name)
        await route_service.assign_driver(route_id, driver2_id)
        route = await route_service.start_route(route_id, driver2_id)
        await stop_service.skip_stop(route_id, route["stops"][0]["id"], driver2_id)
        print(f"  rota olusturuldu: {name}")

    # Rota 4: Tamamlanmis motosiklet teslimati - delivered, 2 delivered stop
    name = "Kaleici Motosiklet Teslimati"
    if await route_exists(route_repo, name):
        print(f"  rota zaten var, atlaniyor: {name}")
    else:
        route = await route_service.create_route(
            RouteCreate(
                origin="Kaleici Depo",
                destination="Kaleici Merkez",
                distance_km=12,
                vehicle_id=moto_id,
                expected_revenue=400,
                assigned_driver_id=driver1_id,
                stops=[
                    {"sequence_number": 1, "customer_name": "Deniz Aydin", "address": "Kaleici Hesapci Sok. No:2"},
                    {"sequence_number": 2, "customer_name": "Selin Celik", "address": "Kaleici Uzun Carsi No:6"},
                ],
            ),
            created_by=admin_id,
        )
        route_id = str(route["_id"])
        await tag_route_with_seed_name(route_repo, route["_id"], name)
        await route_service.assign_driver(route_id, driver1_id)
        route = await route_service.start_route(route_id, driver1_id)
        await stop_service.deliver_stop(
            route_id,
            route["stops"][0]["id"],
            driver1_id,
            StopDeliverRequest(recipient_name="Deniz Aydin", delivery_note="Teslim edildi."),
        )
        # Son durak teslim edilince rota otomatik olarak 'delivered' durumuna geciyor (StopService).
        await stop_service.deliver_stop(
            route_id,
            route["stops"][1]["id"],
            driver1_id,
            StopDeliverRequest(recipient_name="Selin Celik", delivery_note="Teslim edildi."),
        )
        print(f"  rota olusturuldu: {name}")

    # Rota 5: Iptal edilmis rota - cancelled, surucusuz, 1 pending stop
    name = "Iptal Edilmis Kurumsal Teslimat"
    if await route_exists(route_repo, name):
        print(f"  rota zaten var, atlaniyor: {name}")
    else:
        route = await route_service.create_route(
            RouteCreate(
                origin="Lara Depo",
                destination="Lara Kurumsal Merkez",
                distance_km=25,
                vehicle_id=ev_id,
                expected_revenue=600,
                assigned_driver_id=None,
                stops=[
                    {"sequence_number": 1, "customer_name": "Kurumsal Musteri A.S.", "address": "Lara Is Merkezi No:15"},
                ],
            ),
            created_by=admin_id,
        )
        route_id = str(route["_id"])
        await tag_route_with_seed_name(route_repo, route["_id"], name)
        await route_service.cancel_route(route_id)
        print(f"  rota olusturuldu: {name}")


async def seed_audit_log(audit_service: AuditLogService) -> None:
    await audit_service.record(
        actor_user_id=None,
        actor_email="system",
        actor_role=None,
        action=AuditAction.DEMO_SEEDED,
        description="Demo data was seeded.",
        entity_type="demo_data",
        metadata={"users": 4, "vehicles": 4, "routes": 5},
    )
    print("  audit log kaydi olusturuldu: demo_seeded")


async def main() -> None:
    await connect_to_mongo()
    try:
        user_repo = UserRepository()
        vehicle_repo = VehicleRepository()
        route_repo = RouteRepository()
        audit_repo = AuditLogRepository()

        route_service = RouteService(route_repo, vehicle_repo)
        stop_service = StopService(route_repo, route_service)
        audit_service = AuditLogService(audit_repo)

        print("Demo kullanicilar olusturuluyor...")
        users = await seed_users(user_repo)

        print("Demo araclar olusturuluyor...")
        vehicles = await seed_vehicles(vehicle_repo)

        print("Demo rotalar olusturuluyor...")
        await seed_routes(route_repo, route_service, stop_service, users, vehicles)

        print("Audit log kaydediliyor...")
        await seed_audit_log(audit_service)

        print("Demo veri olusturma tamamlandi.")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

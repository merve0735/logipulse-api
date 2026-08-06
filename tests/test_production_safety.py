from datetime import datetime, timezone

import pytest

from app.api.v1.routes import _to_stop_out, to_route_out
from app.core.config import settings
from app.scripts.seed_demo_data import _guard_against_production


def test_seed_guard_blocks_in_production(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.delenv("ALLOW_SEED_IN_PRODUCTION", raising=False)

    with pytest.raises(SystemExit):
        _guard_against_production()


def test_seed_guard_allows_production_with_explicit_override(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setenv("ALLOW_SEED_IN_PRODUCTION", "yes")

    _guard_against_production()  # raise etmemeli


def test_seed_guard_allows_development():
    assert settings.ENVIRONMENT == "development"
    _guard_against_production()  # raise etmemeli


def _minimal_route_doc(**overrides) -> dict:
    from bson import ObjectId

    doc = {
        "_id": ObjectId(),
        "origin": "Depo",
        "destination": "Merkez",
        "distance_km": 10,
        "vehicle_id": "vehicle-1",
        "vehicle_plate_number": "07 AA 001",
        "vehicle_type": "electric_van",
        "expected_revenue": 100,
        "estimated_carbon_kg": 1.0,
        "estimated_cost": 5.0,
        "estimated_profit": 95.0,
        "status": "pending",
        "created_by": "user-1",
        "created_at": datetime.now(timezone.utc),
    }
    doc.update(overrides)
    return doc


def test_route_without_stops_key_does_not_crash():
    # Eski (stops eklenmeden once olusturulmus) bir route dokumanini simule eder.
    doc = _minimal_route_doc()
    assert "stops" not in doc

    route_out = to_route_out(doc)

    assert route_out.stops == []


def test_route_without_assigned_driver_does_not_crash():
    doc = _minimal_route_doc()
    assert "assigned_driver_id" not in doc

    route_out = to_route_out(doc)

    assert route_out.assigned_driver_id is None


def test_stop_with_missing_optional_fields_does_not_crash():
    # Eski bir stop dokumaninda customer_phone, latitude/longitude, package_weight_kg,
    # delivery_note, failure_reason, delivered_at, proof_of_delivery gibi opsiyonel
    # alanlar hic yazilmamis olabilir.
    doc = {
        "id": "stop-1",
        "sequence_number": 1,
        "customer_name": "Test Musteri",
        "address": "Test Adres",
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    stop_out = _to_stop_out(doc)

    assert stop_out.customer_phone is None
    assert stop_out.latitude is None
    assert stop_out.longitude is None
    assert stop_out.package_weight_kg is None
    assert stop_out.delivery_note is None
    assert stop_out.failure_reason is None
    assert stop_out.delivered_at is None
    assert stop_out.proof_of_delivery is None

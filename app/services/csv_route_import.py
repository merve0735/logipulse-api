import csv
import io
from typing import Optional

from app.models.stop import StopCreate


class CsvValidationError(Exception):
    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__("CSV validation failed")


def parse_csv_rows(csv_bytes: bytes) -> list[dict]:
    try:
        text = csv_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise CsvValidationError([_error(0, "file", "CSV dosyası okunamadı, UTF-8 formatında olmalı.")])

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise CsvValidationError([_error(0, "file", "CSV dosyasında hiç satır yok.")])
    return rows


def validate_csv_rows(raw_rows: list[dict]) -> list[StopCreate]:
    errors: list[dict] = []
    stops: list[StopCreate] = []
    seen_sequence_numbers: set[int] = set()

    for row_number, raw_row in enumerate(raw_rows, start=2):  # 1. satır başlık
        row_errors: list[dict] = []

        sequence_number = _parse_int(raw_row.get("sequence_number"), row_number, "sequence_number", row_errors)
        if sequence_number is not None:
            if sequence_number in seen_sequence_numbers:
                row_errors.append(_error(row_number, "sequence_number", "sequence_number bu CSV içinde tekrar ediyor."))
            else:
                seen_sequence_numbers.add(sequence_number)

        customer_name = (raw_row.get("customer_name") or "").strip()
        if not customer_name:
            row_errors.append(_error(row_number, "customer_name", "customer_name zorunludur."))

        address = (raw_row.get("address") or "").strip()
        if not address:
            row_errors.append(_error(row_number, "address", "address zorunludur."))

        latitude = _parse_float(raw_row.get("latitude"), row_number, "latitude", row_errors)
        longitude = _parse_float(raw_row.get("longitude"), row_number, "longitude", row_errors)

        package_weight_kg = _parse_float(raw_row.get("package_weight_kg"), row_number, "package_weight_kg", row_errors)
        if package_weight_kg is not None and package_weight_kg <= 0:
            row_errors.append(_error(row_number, "package_weight_kg", "package_weight_kg 0'dan büyük olmalı."))

        errors.extend(row_errors)

        if not row_errors:
            stops.append(
                StopCreate(
                    sequence_number=sequence_number,
                    customer_name=customer_name,
                    customer_phone=(raw_row.get("customer_phone") or "").strip() or None,
                    address=address,
                    latitude=latitude,
                    longitude=longitude,
                    package_weight_kg=package_weight_kg,
                    delivery_note=(raw_row.get("delivery_note") or "").strip() or None,
                )
            )

    if errors:
        raise CsvValidationError(errors)

    return stops


def _error(row: int, field: str, message: str) -> dict:
    return {"row": row, "field": field, "message": message}


def _parse_int(raw_value: Optional[str], row: int, field: str, row_errors: list[dict]) -> Optional[int]:
    if raw_value is None or raw_value.strip() == "":
        row_errors.append(_error(row, field, f"{field} zorunludur."))
        return None
    try:
        return int(raw_value.strip())
    except ValueError:
        row_errors.append(_error(row, field, f"{field} sayısal (tam sayı) olmalı."))
        return None


def _parse_float(raw_value: Optional[str], row: int, field: str, row_errors: list[dict]) -> Optional[float]:
    if raw_value is None or raw_value.strip() == "":
        row_errors.append(_error(row, field, f"{field} zorunludur."))
        return None
    try:
        return float(raw_value.strip())
    except ValueError:
        row_errors.append(_error(row, field, f"{field} sayısal olmalı."))
        return None

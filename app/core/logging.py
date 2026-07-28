"""
Teknik application logging (audit log ile karistirilmamali).

Audit log kullanici islemlerini (kim ne zaman ne yapti) veritabanina yazar.
Bu modul ise backend terminaline yazilan performans/teknik loglari yonetir:
hangi endpoint cagrildi, ne kadar surdu, hangi islem yavas calisti.
"""

import logging
import sys

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)-8s | %(message)s"
_DATE_FORMAT = "%H:%M:%S"

_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # pymongo/httpx/google-genai kutuphaneleri kendi INFO loglarini basiyor
    # ve terminali gereksiz kalabaliklastiriyor; sadece uyari ve uzerini goster.
    for noisy_logger_name in ("pymongo", "httpx", "httpcore", "google_genai"):
        logging.getLogger(noisy_logger_name).setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def _format_duration(elapsed_ms: float) -> str:
    if elapsed_ms >= 1000:
        return f"{elapsed_ms / 1000:.2f} s"
    return f"{elapsed_ms:.1f} ms"


def log_duration(
    logger: logging.Logger,
    operation_name: str,
    elapsed_ms: float,
    slow_threshold_ms: float = 1000.0,
) -> None:
    """Bir islemin ne kadar surdugunu loglar. Esik asilirsa WARNING, degilse INFO.

    Loglama hicbir zaman ana islemi bozmamali; bu yuzden hata sessizce yutulur.
    """
    try:
        duration_text = _format_duration(elapsed_ms)
        if elapsed_ms >= slow_threshold_ms:
            threshold_text = _format_duration(slow_threshold_ms)
            logger.warning("%s took %s (slow, >%s)", operation_name, duration_text, threshold_text)
        else:
            logger.info("%s took %s", operation_name, duration_text)
    except Exception:
        pass

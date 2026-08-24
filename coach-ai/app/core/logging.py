import logging
import os
import sys
import time
import uuid

from fastapi import Request, Response


SERVICE_NAME = "coach-ai"


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s level=%(levelname)s service="
            f"{SERVICE_NAME} logger=%(name)s message=%(message)s"
        ),
        stream=sys.stdout,
        force=True,
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    for noisy_logger in ("pymongo", "redis", "asyncio"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


async def request_logging_middleware(request: Request, call_next) -> Response:
    logger = logging.getLogger("http")
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    started_at = time.perf_counter()
    method = request.method
    path = request.url.path
    logger.debug(
        "request.started request_id=%s method=%s path=%s",
        request_id,
        method,
        path,
    )
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - started_at) * 1000
        logger.exception(
            "request.unhandled request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id,
            method,
            path,
            duration_ms,
        )
        raise

    duration_ms = (time.perf_counter() - started_at) * 1000
    status_code = response.status_code
    if status_code >= 500:
        log_level = logging.ERROR
    elif status_code >= 400:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO
    logger.log(
        log_level,
        "request.completed request_id=%s method=%s path=%s status=%d duration_ms=%.2f",
        request_id,
        method,
        path,
        status_code,
        duration_ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response

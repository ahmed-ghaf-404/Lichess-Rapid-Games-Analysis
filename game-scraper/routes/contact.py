import asyncio
import base64
import binascii
from collections import defaultdict, deque
from email.message import EmailMessage
from email.utils import parseaddr
import hashlib
import hmac
import logging
import os
import secrets
import smtplib
import ssl
import time

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, ValidationInfo, field_validator


router = APIRouter(prefix="/contact", tags=["contact"])
logger = logging.getLogger(__name__)

MIN_FORM_SECONDS = 2
MAX_FORM_SECONDS = 60 * 60
RATE_LIMIT_WINDOW_SECONDS = 60 * 60
RATE_LIMIT_MESSAGES = 5
_submissions: dict[str, deque[float]] = defaultdict(deque)
_rate_limit_lock = asyncio.Lock()


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    subject: str = Field(default="CCC website message", min_length=3, max_length=150)
    message: str = Field(min_length=20, max_length=4000)
    website: str = Field(default="", max_length=200)
    challenge: str = Field(min_length=20, max_length=500)

    @field_validator("name", "email", "subject")
    @classmethod
    def reject_header_injection(cls, value: str, info: ValidationInfo) -> str:
        cleaned = value.strip()
        if "\r" in cleaned or "\n" in cleaned:
            raise ValueError("Line breaks are not allowed in this field.")
        minimum = {"name": 2, "email": 5, "subject": 3}[info.field_name]
        if len(cleaned) < minimum:
            raise ValueError("This field is too short.")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        _, parsed = parseaddr(value)
        if parsed != value or "@" not in parsed or parsed.startswith("@"):
            raise ValueError("Enter a valid email address.")
        return value

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 20:
            raise ValueError("The message must contain at least 20 characters.")
        return cleaned


def _contact_secret() -> str:
    secret = os.getenv("CONTACT_FORM_SECRET", "")
    if len(secret) < 24:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Contact delivery is not configured.",
        )
    return secret


def _encode_challenge(issued_at: int, nonce: str) -> str:
    payload = f"{issued_at}.{nonce}"
    signature = hmac.new(
        _contact_secret().encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    token = f"{payload}.{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(token).decode("ascii")


def _verify_challenge(token: str) -> None:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        issued_raw, nonce, supplied_signature = decoded.split(".", 2)
        issued_at = int(issued_raw)
    except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The contact form expired. Refresh and try again.",
        ) from exc

    payload = f"{issued_at}.{nonce}"
    expected_signature = hmac.new(
        _contact_secret().encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    age = int(time.time()) - issued_at

    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise HTTPException(status_code=400, detail="Invalid contact form challenge.")
    if age < MIN_FORM_SECONDS:
        raise HTTPException(status_code=400, detail="Please take a moment before sending.")
    if age > MAX_FORM_SECONDS or age < 0:
        raise HTTPException(status_code=400, detail="The contact form expired. Refresh and try again.")


def _client_address(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


async def _check_rate_limit(client_address: str) -> None:
    now = time.monotonic()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    async with _rate_limit_lock:
        attempts = _submissions[client_address]
        while attempts and attempts[0] < cutoff:
            attempts.popleft()
        if len(attempts) >= RATE_LIMIT_MESSAGES:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many messages were sent. Please try again later.",
            )
        attempts.append(now)


def _send_email(payload: ContactRequest) -> None:
    host = os.getenv("SMTP_HOST", "")
    recipient = os.getenv("CONTACT_RECIPIENT", "")
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("CONTACT_SENDER", "") or username
    security_mode = os.getenv("SMTP_SECURITY", "starttls").lower()

    if not host or not recipient or not sender:
        raise RuntimeError("Contact email configuration is incomplete.")

    default_port = 465 if security_mode == "ssl" else 587
    port = int(os.getenv("SMTP_PORT", str(default_port)))

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Reply-To"] = payload.email
    message["Subject"] = f"[CCC Contact] {payload.subject}"
    message.set_content(
        "A message was sent from the Choco Chess Coach contact form.\n\n"
        f"Name: {payload.name}\n"
        f"Reply email: {payload.email}\n\n"
        f"{payload.message}\n"
    )

    context = ssl.create_default_context()
    if security_mode == "ssl":
        smtp: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=15, context=context)
    else:
        smtp = smtplib.SMTP(host, port, timeout=15)

    with smtp:
        smtp.ehlo()
        if security_mode == "starttls":
            smtp.starttls(context=context)
            smtp.ehlo()
        if username:
            smtp.login(username, password)
        smtp.send_message(message)


@router.get("/challenge")
async def contact_challenge(response: Response) -> dict[str, str]:
    response.headers["Cache-Control"] = "no-store"
    token = _encode_challenge(int(time.time()), secrets.token_urlsafe(18))
    return {"challenge": token}


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def submit_contact(payload: ContactRequest, request: Request) -> dict[str, str]:
    if payload.website:
        logger.warning("contact.bot_rejected reason=honeypot")
        raise HTTPException(status_code=400, detail="Unable to send this message.")

    _verify_challenge(payload.challenge)
    await _check_rate_limit(_client_address(request))

    try:
        await asyncio.to_thread(_send_email, payload)
    except Exception as exc:
        logger.exception("contact.delivery_failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The message could not be delivered. Please try again later.",
        ) from exc

    logger.info("contact.delivery_completed")
    return {"status": "accepted", "message": "Your message was sent."}

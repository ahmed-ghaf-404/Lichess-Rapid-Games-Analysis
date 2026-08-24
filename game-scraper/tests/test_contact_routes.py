import asyncio

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from routes import contact as contact_route


FORM_SECRET = "test-contact-form-secret-with-32-characters"


def test_signed_challenge_observes_minimum_form_time(monkeypatch):
    monkeypatch.setenv("CONTACT_FORM_SECRET", FORM_SECRET)
    monkeypatch.setattr(contact_route.time, "time", lambda: 1_000)
    challenge = contact_route._encode_challenge(1_000, "test-nonce")

    monkeypatch.setattr(contact_route.time, "time", lambda: 1_001)
    with pytest.raises(HTTPException) as error:
        contact_route._verify_challenge(challenge)

    assert error.value.status_code == 400
    assert "moment" in error.value.detail

    monkeypatch.setattr(contact_route.time, "time", lambda: 1_002)
    contact_route._verify_challenge(challenge)


def test_malformed_challenge_returns_a_client_error(monkeypatch):
    monkeypatch.setenv("CONTACT_FORM_SECRET", FORM_SECRET)

    with pytest.raises(HTTPException) as error:
        contact_route._verify_challenge("this-is-not-valid-base64%%%%")

    assert error.value.status_code == 400
    assert "expired" in error.value.detail


def test_contact_request_rejects_blank_message_after_trimming():
    with pytest.raises(ValidationError):
        contact_route.ContactRequest(
            name="Test Person",
            email="person@example.com",
            subject="Project question",
            message=" " * 25,
            challenge="x" * 24,
        )


def test_honeypot_is_rejected_before_email_delivery(monkeypatch):
    delivered = False

    def fake_delivery(_payload):
        nonlocal delivered
        delivered = True

    monkeypatch.setattr(contact_route, "_send_email", fake_delivery)
    payload = contact_route.ContactRequest(
        name="Test Person",
        email="person@example.com",
        subject="Project question",
        message="This is a sufficiently long test message.",
        website="https://bot.invalid",
        challenge="x" * 24,
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(contact_route.submit_contact(payload, request=None))

    assert error.value.status_code == 400
    assert delivered is False

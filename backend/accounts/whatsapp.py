"""
Pluggable WhatsApp sender for verification codes.

Backends (settings.WHATSAPP_BACKEND):
  - "console" (default): logs the code — used in development, no provider needed.
  - "twilio": Twilio WhatsApp API.
  - "meta":   Meta WhatsApp Cloud API.

Provider calls use the standard library (urllib) so no extra dependencies are
required. Each returns a dict; a truthy "dev_code" means the code should be
surfaced on screen (console/dev mode only).
"""

from __future__ import annotations

import base64
import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger("accounts")


def _message(code: str) -> str:
    ttl = getattr(settings, "RESET_CODE_TTL_MINUTES", 10)
    return (
        f"Your Savoria password reset code is {code}. "
        f"It expires in {ttl} minutes. If you didn't request this, ignore this message."
    )


def send_whatsapp_code(phone: str, code: str) -> dict:
    """Send a verification code to a WhatsApp number via the configured backend."""
    backend = getattr(settings, "WHATSAPP_BACKEND", "console")
    try:
        if backend == "twilio":
            return _send_twilio(phone, _message(code))
        if backend == "meta":
            return _send_meta(phone, code)
    except Exception:  # noqa: BLE001 — never let delivery errors break the flow
        logger.exception("WhatsApp delivery failed via %s", backend)
        return {"delivered": False, "error": True}

    # Console / development backend.
    logger.info("[WhatsApp DEV] → %s : %s", phone, _message(code))
    return {"delivered": False, "dev_code": code}


def _send_twilio(phone: str, message: str) -> dict:
    sid = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    sender = settings.TWILIO_WHATSAPP_FROM  # e.g. "whatsapp:+14155238886"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data = urllib.parse.urlencode(
        {"From": sender, "To": f"whatsapp:{phone}", "Body": message}
    ).encode()
    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Basic {auth}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        logger.info("Twilio WhatsApp sent (status %s)", resp.status)
    return {"delivered": True}


def _send_meta(phone: str, code: str) -> dict:
    token = settings.WHATSAPP_TOKEN
    phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
    template = settings.WHATSAPP_TEMPLATE_NAME
    url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
    # Business-initiated messages require an approved template.
    payload = {
        "messaging_product": "whatsapp",
        "to": phone.lstrip("+"),
        "type": "template",
        "template": {
            "name": template,
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": code}],
                }
            ],
        },
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST"
    )
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as resp:
        logger.info("Meta WhatsApp sent (status %s)", resp.status)
    return {"delivered": True}

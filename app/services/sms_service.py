import httpx
from app.config import settings


async def send_sms(to: str, message: str, from_name: str = "EMR4") -> dict:
    if not settings.clicksend_username or not settings.clicksend_api_key:
        print(f"[SMS STUB] To: {to} | {message[:80]}")
        return {"status": "stub", "detail": "ClickSend not configured"}

    url = "https://rest.clicksend.com/v3/sms/send"
    payload = {
        "messages": [{"to": to, "body": message, "from": from_name, "source": "EMR4"}]
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url, json=payload,
            auth=(settings.clicksend_username, settings.clicksend_api_key),
            timeout=10,
        )
    return resp.json()

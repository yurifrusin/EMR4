# EMR4 WhatsApp Notifications

This is the preferred fallback channel when Codex/Codex-app push notifications
are unreliable. Use it for Ariadne operational alerts only: sprint closeout,
agent blocker, security review needed, failed verification, or user-decision
points. Do not send PHI, patient identifiers, clinical details, access tokens,
secrets, or raw error payloads.

## Architecture

- Sender: Meta WhatsApp Business Platform Cloud API.
- Local helper: `scripts/notify_yuri_whatsapp.py`.
- Credentials: local `.env` only; never commit access tokens or phone IDs.
- Default mode: approved WhatsApp message template.
- Free-form text mode: available only when WhatsApp's 24-hour service window is
  open after Yuri messages the business number.

## Local Environment Variables

Add these to the repo-local `.env` after Meta setup:

```dotenv
WHATSAPP_ACCESS_TOKEN=<permanent-or-temporary-access-token>
WHATSAPP_PHONE_NUMBER_ID=<Meta phone number ID>
WHATSAPP_TO_NUMBER=<Yuri mobile in E.164 format, digits only or +614...>
WHATSAPP_TEMPLATE_NAME=emr4_ops_alert
WHATSAPP_TEMPLATE_LANGUAGE=en_US
WHATSAPP_GRAPH_VERSION=v24.0
WHATSAPP_DEFAULT_MESSAGE=EMR4 notification. Open Codex for details.
```

`WHATSAPP_TO_NUMBER` should be Yuri's WhatsApp-capable mobile number in
international format, for example `+61412345678`.

## Recommended Template

Create a Utility template named:

```text
emr4_ops_alert
```

Suggested body:

```text
EMR4 Ariadne alert

{{1}}

Status: {{2}}

Action: {{3}}
```

Suggested parameter meanings:

1. Short title, e.g. `Sprint closed`.
2. Safe operational summary, e.g. `Sprint 22 closed and all checks passed`.
3. Required action, e.g. `No action needed` or `Open Codex to approve release`.

## Yuri's Meta Setup Checklist

1. Open [Meta for Developers](https://developers.facebook.com/).
2. Create or select a Meta app.
3. Add the **WhatsApp** product.
4. In **WhatsApp > API Setup**, note:
   - `Phone number ID`
   - temporary access token for initial testing
5. Add Yuri's mobile as a test recipient and complete WhatsApp verification if
   using Meta's test number.
6. In WhatsApp Manager, create the `emr4_ops_alert` Utility template above.
7. Wait for template approval.
8. For durable use, create a System User token with WhatsApp permissions rather
   than relying on a temporary developer token.
9. Paste the values into local `.env`.
10. Ask Ariadne to send a dry run and then a live test.

Official docs:

- [WhatsApp Cloud API Get Started](https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started)
- [WhatsApp template fundamentals](https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/overview)
- [Business phone numbers](https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/phone-numbers)

## Dry Run

From the repo root:

```powershell
python scripts\notify_yuri_whatsapp.py --dry-run --field "Test alert" --field "Dry-run only" --field "No action needed"
```

Expected: JSON payload printed locally. No network call is made.

## Live Template Test

After `.env` values and template approval:

```powershell
python scripts\notify_yuri_whatsapp.py --field "Test alert" --field "WhatsApp notifications are configured" --field "Reply in Codex if received"
```

Expected: Meta returns JSON with a WhatsApp message ID, and Yuri receives the
message.

## Free-Form Text Test

Use only after Yuri has messaged the business number, opening a 24-hour service
window:

```powershell
python scripts\notify_yuri_whatsapp.py --text --message "EMR4 test: free-form service-window message."
```

## Ariadne Usage

Use WhatsApp when:

- sprint closeout completes,
- a blocker needs Yuri's decision,
- a security finding needs human approval,
- an external console/device/manual check is required,
- Codex-app push notifications are unreliable.

Keep messages short and safe. Put details in Codex or repo docs, not WhatsApp.

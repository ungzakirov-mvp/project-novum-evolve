from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.email_service import process_inbound_email
from app.services.telegram_bot import telegram_bot
from pydantic import BaseModel

router = APIRouter(prefix="/webhooks", tags=["Вебхуки"])

class EmailPayload(BaseModel):
    sender: str
    subject: str
    body: str

@router.post("/email/inbound", summary="Симуляция входящего письма")
def receive_email(
    payload: EmailPayload,
    db: Session = Depends(get_db)
):
    """
    Mock endpoint to simulate receiving an email from SendGrid/Mailgun.
    """
    try:
        ticket = process_inbound_email(
            db=db,
            email_from=payload.sender,
            subject=payload.subject,
            body=payload.body
        )
        return {"status": "ok", "ticket_id": ticket.id, "readable_id": ticket.readable_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/telegram", summary="Входящий вебхук от Telegram")
async def telegram_webhook(update: dict = Body(...)):
    """
    Endpoint for Telegram Webhook
    """
    await telegram_bot.handle_update(update)
    return {"status": "ok"}

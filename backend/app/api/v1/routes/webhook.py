from fastapi import APIRouter, Depends, HTTPException
from app.schemas import WebhookRequest, WebhookResponse
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.models import Ticket
from app.database import get_db
from sqlalchemy.orm import Session
from app.adapters.twilio_adapter import TwilioVoiceAdapter
from app.adapters.whatsapp_adapter import handle_whatsapp
from app.adapters.telegram_adapter import handle_telegram
from app.adapters.webchat_adapter import handle_webchat

router = APIRouter()
conv_manager = ConversationManager()
ai_engine = AIEngine()

@router.post("/webhook/voice/{provider}", response_model=WebhookResponse)
def voice_webhook(provider: str, payload: WebhookRequest, db: Session = Depends(get_db)):
    if provider == "twilio":
        # save ticket
        content = payload.recording_url or ""
        sentiment, severity = ai_engine.analyze_text(content)
        ticket = Ticket(channel="voice", user_identifier=payload.user_id,
                        content=content, sentiment=sentiment, severity=severity)
        db.add(ticket); db.commit(); db.refresh(ticket)
        # respond via TwiML
        return {"reply": TwilioVoiceAdapter.handle_call(payload.dict())}
    raise HTTPException(status_code=400, detail="Unknown provider")

@router.post("/webhook/chat/{channel}", response_model=WebhookResponse)
def chat_webhook(channel: str, payload: WebhookRequest, db: Session = Depends(get_db)):
    # translate and analyze
    text = payload.message or ""
    translated = ai_engine.translate_text(text)
    sentiment, severity = ai_engine.analyze_text(translated)
    ticket = Ticket(channel=channel, user_identifier=payload.user_id,
                    content=translated, sentiment=sentiment, severity=severity)
    db.add(ticket); db.commit(); db.refresh(ticket)
    # route to appropriate adapter
    if channel == "whatsapp":
        reply = handle_whatsapp(payload.dict())
    elif channel == "telegram":
        reply = handle_telegram(payload.dict())
    elif channel == "webchat":
        reply = handle_webchat(payload.dict())
    else:
        reply = "Unsupported channel"
    return {"reply": reply}

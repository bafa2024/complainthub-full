from pydantic import BaseModel
from typing import Optional

class WebhookRequest(BaseModel):
    provider: str
    channel: str
    user_id: str
    message: Optional[str]
    recording_url: Optional[str]

class WebhookResponse(BaseModel):
    reply: str

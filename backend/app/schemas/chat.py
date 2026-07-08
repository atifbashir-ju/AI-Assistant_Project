from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message.")
    session_id: Optional[str] = Field(
        default=None,
        description=(
            "Conversation/thread identifier. Send the same session_id on "
            "every message in a conversation so the agent remembers prior "
            "turns. Omit it (or send a new one) to start a fresh conversation."
        ),
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="Optional base64-encoded image to send alongside the message (vision).",
    )
    image_mime_type: Optional[str] = Field(
        default=None,
        description="MIME type of image_base64, e.g. 'image/png' or 'image/jpeg'.",
    )


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class SuggestionsRequest(BaseModel):
    session_id: str


class SuggestionsResponse(BaseModel):
    suggestions: list[str]

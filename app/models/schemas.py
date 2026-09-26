from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant"]

class Message(BaseModel):
    role: Role
    content: str = Field(min_length=1)

class ChatRequest(BaseModel):
    model: str = Field(default="nexora-mock", min_length=1, max_length=128)
    messages: list[Message] = Field(min_length=1, max_length=100)
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_tokens: int = Field(default=256, ge=1, le=4096)
    stream: bool = False

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    id: str
    model: str
    content: str
    provider: str
    usage: Usage
    latency_ms: float

class ProviderInfo(BaseModel):
    name: str
    healthy: bool
    models: list[str]

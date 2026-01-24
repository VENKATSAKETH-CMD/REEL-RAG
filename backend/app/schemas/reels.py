from pydantic import BaseModel


class ReelChatRequest(BaseModel):
    message: str


class ReelChatResponse(BaseModel):
    answer: str

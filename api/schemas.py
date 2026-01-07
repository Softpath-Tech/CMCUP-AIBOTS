from pydantic import BaseModel
from typing import List, Optional

class MenuItem(BaseModel):
    name: str
    value: str

class ChatResponse(BaseModel):
    text: str
    menus: Optional[List[MenuItem]] = []
    isMenusAvailable: bool
    source: str
    session_id: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

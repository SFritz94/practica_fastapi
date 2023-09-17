from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None #Opcional, un campo o el otro
    username: str
    email: str
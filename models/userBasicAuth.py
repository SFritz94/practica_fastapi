from pydantic import BaseModel

class UserBA(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool
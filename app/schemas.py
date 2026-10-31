from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    

class SubscriptionCreate(BaseModel):
    city: str
    route_name: str
    route_uid: str
    direction: int = Field(ge=0, le=1)
    stop_uid: str
    stop_name: str
    notify_minutes: int = Field(default=5, ge=1, le=30)


class SubscriptionOut(SubscriptionCreate):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
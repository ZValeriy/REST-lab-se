from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, List, Dict
from datetime import date, datetime
from enum import Enum
from typing_extensions import Annotated


class StatusEnum(str, Enum):
    new = "new"
    heavy = "heavy"
    light = "light"

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class LoyaltyLevel(str, Enum):
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"

class LanguageEnum(str, Enum):
    ru = "ru"
    en = "en"

LoginStr = Annotated[str, StringConstraints(min_length=5, max_length=20)]
PhoneStr = Annotated[str, StringConstraints(pattern=r'^\+7\d{10}$')]

class Client(BaseModel):
    id: int = Field(..., ge=1, le=9999999)
    login: LoginStr
    status: StatusEnum
    created_at: date
    phone_number: Optional[PhoneStr] = None

class ClientPreferences(BaseModel):
    language: Optional[LanguageEnum] = None
    notifications: Optional[bool] = None

class ClientExtended(Client):
    updated_at: Optional[datetime] = None
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    loyalty_level: Optional[LoyaltyLevel] = None
    last_login_at: Optional[datetime] = None
    preferences: Optional[ClientPreferences] = None
    tags: Optional[List[str]] = None

class ProblemDetails(BaseModel):
    title: str
    details: Optional[str] = None
    errors: Optional[Dict[str, List[str]]] = None
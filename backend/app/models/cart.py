from pydantic import BaseModel, Field


class Cart(BaseModel):
    cart_id: str
    fan_id: str
    seats: int = Field(gt=0)
    section: str
    cart_value: float = Field(gt=0)
    abandoned_hours: float = Field(ge=0)
    lifetime_tickets: int = Field(ge=0)
    days_since_last_purchase: int | None = Field(default=None, ge=0)
    email_opt_in: bool
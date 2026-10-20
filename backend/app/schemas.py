from datetime import datetime
from decimal import Decimal
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, SecretStr, field_validator

class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

def validate_password(value: str) -> str:
    if not 10 <= len(value.encode("utf-8")) <= 72 or not all((re.search(r"[A-Z]", value), re.search(r"[a-z]", value), re.search(r"[0-9]", value), re.search(r"[^A-Za-z0-9]", value))):
        raise ValueError("Usa de 10 a 72 bytes, con mayúscula, minúscula, número y símbolo.")
    return value

class EmailInput(Input):
    email: EmailStr
    @field_validator("email")
    @classmethod
    def normalize(cls, value):
        return str(value).lower()

class RegisterInput(EmailInput):
    name: str = Field(min_length=2, max_length=100)
    password: SecretStr
    @field_validator("password")
    @classmethod
    def password_policy(cls, value):
        validate_password(value.get_secret_value())
        return value

class LoginInput(EmailInput):
    password: SecretStr = Field(min_length=1, max_length=72)

class ResetInput(Input):
    token: str = Field(min_length=20, max_length=200)
    password: SecretStr
    _password_policy = field_validator("password")(RegisterInput.password_policy.__func__)

class ChangePasswordInput(Input):
    current_password: SecretStr = Field(min_length=1, max_length=72)
    password: SecretStr
    _password_policy = field_validator("password")(RegisterInput.password_policy.__func__)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    role: Literal["cliente", "administrador"]
    created_at: datetime
    updated_at: datetime

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class Message(BaseModel):
    message: str

class ProductInput(Input):
    name: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=3, max_length=2000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0, le=1000000, strict=True)
    image_url: HttpUrl = Field(max_length=2000)
    is_active: bool = True

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    price: Decimal
    stock: int
    image_url: str
    is_active: bool

class QuantityInput(Input):
    quantity: int = Field(gt=0, le=1000000, strict=True)

class CartAddInput(QuantityInput):
    product_id: int = Field(gt=0, strict=True)

class CartLineOut(BaseModel):
    product: ProductOut
    quantity: int
    subtotal: Decimal

class CartOut(BaseModel):
    items: list[CartLineOut]
    total: Decimal

class OrderLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int

class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    total: Decimal
    created_at: datetime
    updated_at: datetime
    items: list[OrderLineOut]

class OrderStatusInput(Input):
    status: Literal["pendiente", "confirmado", "enviado", "entregado", "cancelado"]

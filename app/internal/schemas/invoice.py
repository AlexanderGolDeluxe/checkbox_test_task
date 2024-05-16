from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    NonNegativeFloat,
    NonNegativeInt)

from app.internal.schemas import (
    PaymentCreate, PaymentSchema, ProductCreate, UserSchema)

total_round = lambda value: round(value, 2)


class InvoiceItemCreate(ProductCreate):
    quantity: NonNegativeInt = 1


class InvoiceItemBase(BaseModel):
    invoice_id: int
    product_id: int
    quantity: NonNegativeInt = 1
    total: Annotated[NonNegativeFloat, AfterValidator(total_round)]


class InvoiceItemSchema(InvoiceItemCreate):
    total: Annotated[NonNegativeFloat, AfterValidator(total_round)]


class InvoiceCreate(BaseModel):
    products: list[InvoiceItemCreate]
    payment: PaymentCreate | None
    

class InvoiceSchema(BaseModel):
    id: int
    products: list[InvoiceItemSchema]
    payment: PaymentSchema | None
    total: Annotated[NonNegativeFloat, AfterValidator(total_round)]
    rest: Annotated[NonNegativeFloat, AfterValidator(total_round)]
    created_at: datetime
    created_by: UserSchema


class PaginationInfo(BaseModel):
    current_page: NonNegativeInt = 0
    limit: NonNegativeInt | None
    last_page: NonNegativeInt = 0


class InvoicesSchema(PaginationInfo):
    invoices: list[InvoiceSchema]

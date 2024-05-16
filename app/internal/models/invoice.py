from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.internal.models import Base

if TYPE_CHECKING:
    from app.internal.models import Payment, Product, User


class Invoice(Base):
    __tablename__ = "invoice"

    products: Mapped[list["InvoiceItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )
    payment: Mapped["Payment"] = relationship(
        back_populates="invoice", cascade="all"
    )
    total: Mapped[float] = mapped_column(
        Float(asdecimal=True, decimal_return_scale=2)
    )
    rest: Mapped[float] = mapped_column(
        Float(asdecimal=True, decimal_return_scale=2)
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user_owner: Mapped["User"] = relationship(back_populates="invoices")


class InvoiceItem(Base):
    __tablename__ = "invoice_item"

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoice.id", ondelete="CASCADE")
    )
    invoice: Mapped["Invoice"] = relationship(
        back_populates="products", innerjoin=True
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    product: Mapped["Product"] = relationship(cascade="all")
    quantity: Mapped[int] = mapped_column(default=1)
    total: Mapped[float] = mapped_column(
        Float(asdecimal=True, decimal_return_scale=2))

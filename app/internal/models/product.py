from sqlalchemy import Float
from sqlalchemy.orm import Mapped, mapped_column

from app.internal.models import Base


class Product(Base):
    __tablename__ = "product"

    name: Mapped[str]
    price: Mapped[float] = mapped_column(
        Float(asdecimal=True, decimal_return_scale=2)
    )
    description: Mapped[str | None]

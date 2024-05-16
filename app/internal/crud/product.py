from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.models import Product
from app.internal.schemas import ProductCreate


@logger.catch(reraise=bool)
async def create_product(
        session: AsyncSession, product_in: ProductCreate
    ):
    """
    Inserts new row into `product` table if its unique,
    otherwise returns ID of the row from database
    """
    stmt = select(Product).where(
        Product.name == product_in.name and
        Product.price == product_in.price
    )
    product = await session.scalar(stmt)
    if product is None:
        product = Product(**product_in.model_dump())
        session.add(product)
        await session.commit()

    return product.id

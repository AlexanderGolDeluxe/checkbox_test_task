from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.models import Payment
from app.internal.schemas import PaymentCreate


@logger.catch(reraise=bool)
async def create_payment(
        session: AsyncSession, payment_in: PaymentCreate
    ):
    """Inserts new row in `payment` table"""
    payment = Payment(**payment_in.model_dump())
    session.add(payment)
    await session.commit()
    return payment

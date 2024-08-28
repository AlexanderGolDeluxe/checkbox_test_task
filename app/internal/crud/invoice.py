import math
from typing import Literal

from fastapi import HTTPException, status
from loguru import logger
from pydantic import NonNegativeInt, NonNegativeFloat
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload, load_only, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.crud.payment import create_payment
from app.internal.crud.product import create_product
from app.internal.models import Invoice, InvoiceItem, Payment, User
from app.internal.schemas import (
    InvoiceCreate,
    InvoiceSchema,
    InvoiceItemBase,
    InvoiceItemSchema,
    InvoicesSchema,
    PaymentBase,
    PaymentSchema,
    ProductCreate,
    UserSchema
)
from app.utils.prettify_invoice import invoice_to_ticket_format
from app.utils.work_with_dates import parse_like_date


@logger.catch(reraise=True)
async def create_invoice_item(
        session: AsyncSession, invoice_item_in: InvoiceItemBase
    ):
    """Inserts new row in `invoice_item` table"""
    invoice_item = InvoiceItem(**invoice_item_in.model_dump())
    session.add(invoice_item)
    await session.commit()
    return invoice_item


@logger.catch(reraise=True)
async def generate_invoice(
        session: AsyncSession,
        invoice_in: InvoiceCreate,
        created_by: UserSchema
    ):
    """
    Validates invoice data from user,
    calculates remaining fields and generates the invoice,
    after that saving it in database
    """
    created_invoice = dict(
        created_by=created_by,
        products=list(),
        total=sum(
            product.price * product.quantity
            for product in invoice_in.products)
    )
    created_invoice["rest"] = (
        invoice_in.payment.amount - created_invoice["total"]
    )
    if created_invoice["rest"] < 0:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid invoice data. "
                f"Payment amount ({invoice_in.payment.amount}) canʼt be "
                f"less than total ({created_invoice['total']})"))

    invoice = Invoice(
        total=created_invoice["total"],
        rest=created_invoice["rest"],
        created_by=created_by.id
    )
    session.add(invoice)
    await session.commit()
    created_invoice.update(id=invoice.id, created_at=invoice.created_at)

    # Insert payment
    payment_in = PaymentBase(
        invoice_id=invoice.id,
        **invoice_in.payment.model_dump()
    )
    created_payment = await create_payment(session, payment_in)
    created_invoice["payment"] = PaymentSchema(
        id=created_payment.id, **invoice_in.payment.model_dump())

    # Insert product with invoice item
    for product in invoice_in.products:
        product_id = await create_product(session, ProductCreate(
            **product.model_dump(exclude={"quantity"}))
        )
        invoice_item_in = InvoiceItemBase(
            invoice_id=invoice.id,
            product_id=product_id,
            quantity=product.quantity,
            total=product.price * product.quantity
        )
        created_invoice["products"].append(
            InvoiceItemSchema(
                total=invoice_item_in.total, **product.model_dump())
        )
        await create_invoice_item(session, invoice_item_in)

    return InvoiceSchema(**created_invoice)


@logger.catch(reraise=True)
async def select_invoices(session: AsyncSession, where_clauses: list):
    """Executes query to search for invoices using received filters"""
    stmt = (
        select(Invoice)
        .options(
            load_only(Invoice.total, Invoice.rest, Invoice.created_at)
        )
        .join(Invoice.payment)
        .options(
            contains_eager(Invoice.payment)
            .options(load_only(Payment.type, Payment.amount))
        )
        .options(
            joinedload(Invoice.user_owner)
            .options(load_only(User.name, User.login))
        )
        .join(Invoice.products)
        .options(
            contains_eager(Invoice.products)
            .load_only(InvoiceItem.quantity, InvoiceItem.total)
            .joinedload(InvoiceItem.product)
        )
        .where(*where_clauses)
        .order_by(desc(Invoice.created_at))
    )
    result = (await session.scalars(stmt)).unique().all()
    # Preparing to pydantic InvoiceSchema model
    for row in result:
        row.created_by = row.user_owner
        for product in row.products:
            product.name = product.product.name
            product.price = product.product.price
            product.description = product.product.description

    return result


@logger.catch(reraise=True)
async def get_invoices(
        session: AsyncSession,
        owner_id: int,
        from_created_at: str | None,
        to_created_at: str | None,
        max_total: NonNegativeFloat | None,
        min_total: NonNegativeFloat | None,
        payment_type: Literal["cash", "cashless"] | None,
        page: NonNegativeInt,
        limit: NonNegativeInt | None
    ):
    """
    Converts filters from user into where clauses, sends them to query.
    Generates pagination data and append it to response
    """
    where_clauses = [Invoice.created_by == owner_id]
    if from_created_at is not None:
        where_clauses.append(
            Invoice.created_at >= parse_like_date(from_created_at))

    if to_created_at is not None:
        where_clauses.append(
            Invoice.created_at <= parse_like_date(to_created_at))

    if max_total is not None:
        where_clauses.append(Invoice.total <= max_total)

    if min_total is not None:
        where_clauses.append(Invoice.total >= min_total)

    if payment_type is not None:
        where_clauses.append(Payment.type == payment_type)

    response = InvoicesSchema.model_validate(
        dict(
            limit=limit,
            invoices=await select_invoices(session, where_clauses)
        ),
        from_attributes=True
    )
    if limit:
        response.current_page = page
        response.last_page = (
            math.ceil(len(response.invoices) / limit) - 1
        )
        response.invoices = (
            response.invoices[page * limit:(page + 1) * limit])

    return response


@logger.catch(reraise=True)
async def get_pretty_invoice(session: AsyncSession, invoice_id: int):
    """
    Finds for invoice by specified ID
    and returns it in `plain/text` format
    """
    invoices = await select_invoices(session, [Invoice.id == invoice_id])
    if not invoices:
        await session.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID = {invoice_id} not found")

    return invoice_to_ticket_format(invoices[0])

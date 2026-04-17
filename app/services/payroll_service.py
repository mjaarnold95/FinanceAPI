from __future__ import annotations
from decimal import Decimal
from datetime import date
from sqlmodel import Session, select
from app.models.payroll import PayPeriod, PayStub, PayStubLineItem, PayStubLineType
from app.schemas.payroll import PayPeriodCreate, PayStubCreate, YTDSummary


def create_pay_period(data: PayPeriodCreate, session: Session) -> PayPeriod:
    period = PayPeriod(**data.model_dump())
    session.add(period)
    session.commit()
    session.refresh(period)
    return period


def get_pay_period(period_id: int, session: Session) -> PayPeriod | None:
    return session.get(PayPeriod, period_id)


def get_pay_periods(session: Session) -> list[PayPeriod]:
    return list(session.exec(select(PayPeriod)).all())


def create_pay_stub(period_id: int, data: PayStubCreate, session: Session) -> PayStub:
    stub = PayStub(
        pay_period_id=period_id,
        gross_pay=data.gross_pay,
        net_pay=data.net_pay,
        total_taxes=data.total_taxes,
        total_deductions=data.total_deductions,
        notes=data.notes,
    )
    session.add(stub)
    session.flush()
    for item_data in data.line_items:
        item = PayStubLineItem(
            pay_stub_id=stub.id,
            **item_data.model_dump(),
        )
        session.add(item)
    session.commit()
    session.refresh(stub)
    return stub


def get_pay_stub(stub_id: int, session: Session) -> PayStub | None:
    return session.get(PayStub, stub_id)


def get_pay_stubs_for_period(period_id: int, session: Session) -> list[PayStub]:
    stmt = select(PayStub).where(PayStub.pay_period_id == period_id)
    return list(session.exec(stmt).all())


def get_ytd_summary(year: int, session: Session) -> YTDSummary:
    stmt = (
        select(PayStub)
        .join(PayPeriod, PayStub.pay_period_id == PayPeriod.id)
        .where(PayPeriod.pay_date >= date(year, 1, 1))
        .where(PayPeriod.pay_date <= date(year, 12, 31))
    )
    stubs = list(session.exec(stmt).all())
    total_gross = sum(Decimal(str(s.gross_pay)) for s in stubs)
    total_net = sum(Decimal(str(s.net_pay)) for s in stubs)
    total_taxes = sum(Decimal(str(s.total_taxes)) for s in stubs)
    total_deductions = sum(Decimal(str(s.total_deductions)) for s in stubs)
    by_category: dict[str, Decimal] = {}
    for stub in stubs:
        for item in stub.line_items:
            key = f"{item.line_type.value}:{item.description}"
            by_category[key] = by_category.get(key, Decimal("0")) + Decimal(str(item.amount))
    return YTDSummary(
        year=year,
        total_gross_pay=total_gross,
        total_net_pay=total_net,
        total_taxes=total_taxes,
        total_deductions=total_deductions,
        by_category=by_category,
    )

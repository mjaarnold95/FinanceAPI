from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.retirement import RetirementAccount, RetirementContribution
from app.schemas.retirement import (
    RetirementAccountCreate, RetirementAccountUpdate, RetirementContributionCreate,
    YTDContributionSummary, RetirementProjectionRequest, RetirementProjectionResponse
)


def create_retirement_account(data: RetirementAccountCreate, session: Session) -> RetirementAccount:
    account = RetirementAccount(**data.model_dump())
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def get_retirement_account(account_id: int, session: Session) -> Optional[RetirementAccount]:
    return session.get(RetirementAccount, account_id)


def get_retirement_accounts(session: Session) -> list[RetirementAccount]:
    return list(session.exec(select(RetirementAccount)).all())


def update_retirement_account(account_id: int, data: RetirementAccountUpdate, session: Session) -> Optional[RetirementAccount]:
    account = session.get(RetirementAccount, account_id)
    if not account:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
    account.updated_at = datetime.utcnow()
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def add_contribution(account_id: int, data: RetirementContributionCreate, session: Session) -> RetirementContribution:
    account = session.get(RetirementAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Retirement account not found")
    contribution = RetirementContribution(retirement_account_id=account_id, **data.model_dump())
    session.add(contribution)
    total = Decimal(str(data.employee_contribution)) + Decimal(str(data.employer_contribution))
    account.current_balance = Decimal(str(account.current_balance)) + total
    account.updated_at = datetime.utcnow()
    session.add(account)
    session.commit()
    session.refresh(contribution)
    return contribution


def get_contributions_for_account(account_id: int, session: Session) -> list[RetirementContribution]:
    stmt = select(RetirementContribution).where(RetirementContribution.retirement_account_id == account_id)
    return list(session.exec(stmt).all())


def calculate_ytd_contributions(account_id: int, year: int, session: Session) -> YTDContributionSummary:
    account = session.get(RetirementAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Retirement account not found")
    stmt = (
        select(RetirementContribution)
        .where(RetirementContribution.retirement_account_id == account_id)
        .where(RetirementContribution.date >= date(year, 1, 1))
        .where(RetirementContribution.date <= date(year, 12, 31))
    )
    contributions = list(session.exec(stmt).all())
    total_employee = sum(Decimal(str(c.employee_contribution)) for c in contributions)
    total_employer = sum(Decimal(str(c.employer_contribution)) for c in contributions)
    total = total_employee + total_employer
    limit = Decimal(str(account.annual_contribution_limit))
    return YTDContributionSummary(
        year=year,
        account_id=account_id,
        account_name=account.name,
        total_employee_contributions=total_employee,
        total_employer_contributions=total_employer,
        total_contributions=total,
        annual_limit=limit,
        remaining_limit=max(limit - total_employee, Decimal("0")),
    )


def project_retirement_balance(
    account_id: int,
    request: RetirementProjectionRequest,
    session: Session,
) -> RetirementProjectionResponse:
    account = session.get(RetirementAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Retirement account not found")
    pv = Decimal(str(account.current_balance))
    r = request.annual_return_rate
    n = request.years
    pmt = request.additional_annual_contribution
    # FV = PV*(1+r)^n + PMT*((1+r)^n - 1)/r
    growth_factor = (1 + r) ** n
    fv_pv = pv * growth_factor
    if r > 0:
        fv_pmt = pmt * (growth_factor - 1) / r
    else:
        fv_pmt = pmt * n
    projected_balance = fv_pv + fv_pmt
    total_contributions = pmt * n
    total_growth = projected_balance - pv - total_contributions
    return RetirementProjectionResponse(
        account_id=account_id,
        account_name=account.name,
        current_balance=pv,
        years=n,
        annual_return_rate=r,
        additional_annual_contribution=pmt,
        projected_balance=projected_balance.quantize(Decimal("0.01")),
        total_contributions=total_contributions,
        total_growth=total_growth.quantize(Decimal("0.01")),
    )

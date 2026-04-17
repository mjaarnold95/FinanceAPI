from __future__ import annotations
from decimal import Decimal
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.tax import TaxYear, TaxDeduction, TaxPayment, FilingStatus, DeductionType
from app.schemas.tax import TaxYearCreate, TaxYearUpdate, TaxDeductionCreate, TaxPaymentCreate, TaxSummary

# 2024 Federal Tax Brackets
TAX_BRACKETS = {
    FilingStatus.SINGLE: [
        (Decimal("11600"), Decimal("0.10")),
        (Decimal("47150"), Decimal("0.12")),
        (Decimal("100525"), Decimal("0.22")),
        (Decimal("191950"), Decimal("0.24")),
        (Decimal("243725"), Decimal("0.32")),
        (Decimal("609350"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    FilingStatus.MARRIED_FILING_JOINTLY: [
        (Decimal("23200"), Decimal("0.10")),
        (Decimal("94300"), Decimal("0.12")),
        (Decimal("201050"), Decimal("0.22")),
        (Decimal("383900"), Decimal("0.24")),
        (Decimal("487450"), Decimal("0.32")),
        (Decimal("731200"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    FilingStatus.MARRIED_FILING_SEPARATELY: [
        (Decimal("11600"), Decimal("0.10")),
        (Decimal("47150"), Decimal("0.12")),
        (Decimal("100525"), Decimal("0.22")),
        (Decimal("191950"), Decimal("0.24")),
        (Decimal("243725"), Decimal("0.32")),
        (Decimal("365600"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (Decimal("16550"), Decimal("0.10")),
        (Decimal("63100"), Decimal("0.12")),
        (Decimal("100500"), Decimal("0.22")),
        (Decimal("191950"), Decimal("0.24")),
        (Decimal("243700"), Decimal("0.32")),
        (Decimal("609350"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    FilingStatus.QUALIFYING_WIDOW: [
        (Decimal("23200"), Decimal("0.10")),
        (Decimal("94300"), Decimal("0.12")),
        (Decimal("201050"), Decimal("0.22")),
        (Decimal("383900"), Decimal("0.24")),
        (Decimal("487450"), Decimal("0.32")),
        (Decimal("731200"), Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
}

STANDARD_DEDUCTIONS_2024 = {
    FilingStatus.SINGLE: Decimal("14600"),
    FilingStatus.MARRIED_FILING_JOINTLY: Decimal("29200"),
    FilingStatus.MARRIED_FILING_SEPARATELY: Decimal("14600"),
    FilingStatus.HEAD_OF_HOUSEHOLD: Decimal("21900"),
    FilingStatus.QUALIFYING_WIDOW: Decimal("29200"),
}


def _calculate_tax_from_brackets(taxable_income: Decimal, filing_status: FilingStatus) -> tuple[Decimal, Decimal]:
    """Returns (total_tax, marginal_rate)."""
    brackets = TAX_BRACKETS.get(filing_status, TAX_BRACKETS[FilingStatus.SINGLE])
    total_tax = Decimal("0")
    prev_limit = Decimal("0")
    marginal_rate = Decimal("0")
    for limit, rate in brackets:
        if limit is None:
            if taxable_income > prev_limit:
                total_tax += (taxable_income - prev_limit) * rate
                marginal_rate = rate
            break
        if taxable_income <= limit:
            total_tax += (taxable_income - prev_limit) * rate
            marginal_rate = rate
            break
        total_tax += (limit - prev_limit) * rate
        marginal_rate = rate
        prev_limit = limit
    return total_tax, marginal_rate


def create_tax_year(data: TaxYearCreate, session: Session) -> TaxYear:
    tax_year = TaxYear(**data.model_dump())
    session.add(tax_year)
    session.commit()
    session.refresh(tax_year)
    return tax_year


def get_tax_year(tax_year_id: int, session: Session) -> TaxYear | None:
    return session.get(TaxYear, tax_year_id)


def get_tax_years(session: Session) -> list[TaxYear]:
    return list(session.exec(select(TaxYear)).all())


def update_tax_year(tax_year_id: int, data: TaxYearUpdate, session: Session) -> TaxYear | None:
    tax_year = session.get(TaxYear, tax_year_id)
    if not tax_year:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tax_year, key, value)
    session.add(tax_year)
    session.commit()
    session.refresh(tax_year)
    return tax_year


def add_deduction(tax_year_id: int, data: TaxDeductionCreate, session: Session) -> TaxDeduction:
    tax_year = session.get(TaxYear, tax_year_id)
    if not tax_year:
        raise HTTPException(status_code=404, detail="Tax year not found")
    deduction = TaxDeduction(tax_year_id=tax_year_id, **data.model_dump())
    session.add(deduction)
    session.commit()
    session.refresh(deduction)
    return deduction


def remove_deduction(tax_year_id: int, deduction_id: int, session: Session) -> bool:
    deduction = session.get(TaxDeduction, deduction_id)
    if not deduction or deduction.tax_year_id != tax_year_id:
        return False
    session.delete(deduction)
    session.commit()
    return True


def add_payment(tax_year_id: int, data: TaxPaymentCreate, session: Session) -> TaxPayment:
    tax_year = session.get(TaxYear, tax_year_id)
    if not tax_year:
        raise HTTPException(status_code=404, detail="Tax year not found")
    payment = TaxPayment(tax_year_id=tax_year_id, **data.model_dump())
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


def remove_payment(tax_year_id: int, payment_id: int, session: Session) -> bool:
    payment = session.get(TaxPayment, payment_id)
    if not payment or payment.tax_year_id != tax_year_id:
        return False
    session.delete(payment)
    session.commit()
    return True


def calculate_tax_summary(tax_year_id: int, gross_income: Decimal, session: Session) -> TaxSummary:
    tax_year = session.get(TaxYear, tax_year_id)
    if not tax_year:
        raise HTTPException(status_code=404, detail="Tax year not found")
    adjustments = Decimal("0")
    agi = gross_income - adjustments
    if tax_year.deduction_type == DeductionType.STANDARD:
        deduction_amount = STANDARD_DEDUCTIONS_2024.get(tax_year.filing_status, STANDARD_DEDUCTIONS_2024[FilingStatus.SINGLE])
    else:
        deduction_amount = sum(Decimal(str(d.amount)) for d in tax_year.deductions)
    taxable_income = max(agi - deduction_amount, Decimal("0"))
    estimated_tax, marginal_rate = _calculate_tax_from_brackets(taxable_income, tax_year.filing_status)
    total_payments = sum(Decimal(str(p.amount)) for p in tax_year.payments)
    balance = total_payments - estimated_tax
    effective_rate = (estimated_tax / gross_income).quantize(Decimal("0.0001")) if gross_income > 0 else Decimal("0")
    return TaxSummary(
        year=tax_year.year,
        filing_status=tax_year.filing_status,
        gross_income=gross_income,
        adjustments=adjustments,
        agi=agi,
        deduction_amount=deduction_amount,
        taxable_income=taxable_income,
        estimated_tax=estimated_tax.quantize(Decimal("0.01")),
        total_payments=total_payments,
        balance_due_or_refund=balance.quantize(Decimal("0.01")),
        effective_tax_rate=effective_rate,
        marginal_tax_rate=marginal_rate,
    )

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.schemas.tax import (
    TaxYearCreate, TaxYearRead, TaxYearUpdate,
    TaxDeductionCreate, TaxDeductionRead,
    TaxPaymentCreate, TaxPaymentRead, TaxSummary
)
from app.services import tax_service

router = APIRouter()


@router.post("/tax-years", response_model=TaxYearRead, status_code=201)
def create_tax_year(data: TaxYearCreate, session: Session = Depends(get_session)):
    return tax_service.create_tax_year(data, session)


@router.get("/tax-years", response_model=list[TaxYearRead])
def list_tax_years(session: Session = Depends(get_session)):
    return tax_service.get_tax_years(session)


@router.get("/tax-years/{tax_year_id}", response_model=TaxYearRead)
def get_tax_year(tax_year_id: int, session: Session = Depends(get_session)):
    tax_year = tax_service.get_tax_year(tax_year_id, session)
    if not tax_year:
        raise HTTPException(status_code=404, detail="Tax year not found")
    return tax_year


@router.patch("/tax-years/{tax_year_id}", response_model=TaxYearRead)
def update_tax_year(tax_year_id: int, data: TaxYearUpdate, session: Session = Depends(get_session)):
    tax_year = tax_service.update_tax_year(tax_year_id, data, session)
    if not tax_year:
        raise HTTPException(status_code=404, detail="Tax year not found")
    return tax_year


@router.post("/tax-years/{tax_year_id}/deductions", response_model=TaxDeductionRead, status_code=201)
def add_deduction(tax_year_id: int, data: TaxDeductionCreate, session: Session = Depends(get_session)):
    return tax_service.add_deduction(tax_year_id, data, session)


@router.delete("/tax-years/{tax_year_id}/deductions/{deduction_id}", status_code=204)
def remove_deduction(tax_year_id: int, deduction_id: int, session: Session = Depends(get_session)):
    success = tax_service.remove_deduction(tax_year_id, deduction_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Deduction not found")


@router.post("/tax-years/{tax_year_id}/payments", response_model=TaxPaymentRead, status_code=201)
def add_payment(tax_year_id: int, data: TaxPaymentCreate, session: Session = Depends(get_session)):
    return tax_service.add_payment(tax_year_id, data, session)


@router.get("/tax-years/{tax_year_id}/summary", response_model=TaxSummary)
def get_tax_summary(
    tax_year_id: int,
    gross_income: Decimal = Query(..., description="Gross income for the year"),
    session: Session = Depends(get_session),
):
    return tax_service.calculate_tax_summary(tax_year_id, gross_income, session)

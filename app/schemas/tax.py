from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.tax import FilingStatus, DeductionType, TaxPaymentType


class TaxYearCreate(BaseModel):
    year: int
    filing_status: FilingStatus
    deduction_type: DeductionType = DeductionType.STANDARD
    exemptions: int = 1
    notes: Optional[str] = None


class TaxYearUpdate(BaseModel):
    filing_status: Optional[FilingStatus] = None
    deduction_type: Optional[DeductionType] = None
    exemptions: Optional[int] = None
    notes: Optional[str] = None


class TaxDeductionCreate(BaseModel):
    description: str
    amount: Decimal
    category: str
    notes: Optional[str] = None


class TaxDeductionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tax_year_id: int
    description: str
    amount: Decimal
    category: str
    notes: Optional[str] = None


class TaxPaymentCreate(BaseModel):
    payment_date: date
    amount: Decimal
    payment_type: TaxPaymentType
    notes: Optional[str] = None


class TaxPaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tax_year_id: int
    payment_date: date
    amount: Decimal
    payment_type: TaxPaymentType
    notes: Optional[str] = None


class TaxYearRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    year: int
    filing_status: FilingStatus
    deduction_type: DeductionType
    exemptions: int
    notes: Optional[str] = None
    created_at: datetime
    deductions: list[TaxDeductionRead] = []
    payments: list[TaxPaymentRead] = []


class TaxSummary(BaseModel):
    year: int
    filing_status: FilingStatus
    gross_income: Decimal
    adjustments: Decimal
    agi: Decimal
    deduction_amount: Decimal
    taxable_income: Decimal
    estimated_tax: Decimal
    total_payments: Decimal
    balance_due_or_refund: Decimal
    effective_tax_rate: Decimal
    marginal_tax_rate: Decimal

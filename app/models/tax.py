from enum import Enum
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Numeric, Column
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class FilingStatus(str, Enum):
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"
    MARRIED_FILING_SEPARATELY = "married_filing_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"
    QUALIFYING_WIDOW = "qualifying_widow"


class DeductionType(str, Enum):
    STANDARD = "standard"
    ITEMIZED = "itemized"


class TaxPaymentType(str, Enum):
    WITHHOLDING = "withholding"
    ESTIMATED_QUARTERLY = "estimated_quarterly"
    EXTENSION = "extension"
    BALANCE_DUE = "balance_due"
    REFUND = "refund"


class TaxYear(SQLModel, table=True):
    __tablename__ = "tax_years"
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int = Field(index=True)
    filing_status: FilingStatus
    deduction_type: DeductionType = Field(default=DeductionType.STANDARD)
    exemptions: int = Field(default=1)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deductions: list["TaxDeduction"] = Relationship(back_populates="tax_year")
    payments: list["TaxPayment"] = Relationship(back_populates="tax_year")


class TaxDeduction(SQLModel, table=True):
    __tablename__ = "tax_deductions"
    id: Optional[int] = Field(default=None, primary_key=True)
    tax_year_id: int = Field(foreign_key="tax_years.id")
    description: str
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    category: str
    notes: Optional[str] = None
    tax_year: Optional[TaxYear] = Relationship(back_populates="deductions")


class TaxPayment(SQLModel, table=True):
    __tablename__ = "tax_payments"
    id: Optional[int] = Field(default=None, primary_key=True)
    tax_year_id: int = Field(foreign_key="tax_years.id")
    payment_date: date
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    payment_type: TaxPaymentType
    notes: Optional[str] = None
    tax_year: Optional[TaxYear] = Relationship(back_populates="payments")

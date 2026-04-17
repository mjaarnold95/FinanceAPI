from enum import StrEnum
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Numeric, Column
from sqlmodel import SQLModel, Field, Relationship


class FilingStatus(StrEnum):
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"
    MARRIED_FILING_SEPARATELY = "married_filing_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"
    QUALIFYING_WIDOW = "qualifying_widow"


class DeductionType(StrEnum):
    STANDARD = "standard"
    ITEMIZED = "itemized"


class TaxPaymentType(StrEnum):
    WITHHOLDING = "withholding"
    ESTIMATED_QUARTERLY = "estimated_quarterly"
    EXTENSION = "extension"
    BALANCE_DUE = "balance_due"
    REFUND = "refund"


class TaxYear(SQLModel, table=True):
    __tablename__ = "tax_years"
    id: int | None = Field(default=None, primary_key=True)
    year: int = Field(index=True)
    filing_status: FilingStatus
    deduction_type: DeductionType = Field(default=DeductionType.STANDARD)
    exemptions: int = Field(default=1)
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deductions: list["TaxDeduction"] = Relationship(back_populates="tax_year")
    payments: list["TaxPayment"] = Relationship(back_populates="tax_year")


class TaxDeduction(SQLModel, table=True):
    __tablename__ = "tax_deductions"
    id: int | None = Field(default=None, primary_key=True)
    tax_year_id: int = Field(foreign_key="tax_years.id")
    description: str
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    category: str
    notes: str | None = None
    tax_year: TaxYear | None = Relationship(back_populates="deductions")


class TaxPayment(SQLModel, table=True):
    __tablename__ = "tax_payments"
    id: int | None = Field(default=None, primary_key=True)
    tax_year_id: int = Field(foreign_key="tax_years.id")
    payment_date: date
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    payment_type: TaxPaymentType
    notes: str | None = None
    tax_year: TaxYear | None = Relationship(back_populates="payments")

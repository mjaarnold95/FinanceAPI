from enum import StrEnum
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Numeric, Column
from sqlmodel import SQLModel, Field, Relationship


class RetirementAccountType(StrEnum):
    TRADITIONAL_401K = "traditional_401k"
    ROTH_401K = "roth_401k"
    TRADITIONAL_403B = "traditional_403b"
    ROTH_403B = "roth_403b"
    TRADITIONAL_457B = "traditional_457b"
    ROTH_457B = "roth_457b"
    TRADITIONAL_IRA = "traditional_ira"
    ROTH_IRA = "roth_ira"
    SEP_IRA = "sep_ira"
    SIMPLE_IRA = "simple_ira"
    PENSION = "pension"
    HSA = "hsa"
    OTHER = "other"


class ContributionType(StrEnum):
    EMPLOYEE_PRETAX = "employee_pretax"
    EMPLOYEE_ROTH = "employee_roth"
    EMPLOYEE_AFTER_TAX = "employee_after_tax"
    EMPLOYER_MATCH = "employer_match"
    EMPLOYER_PROFIT_SHARING = "employer_profit_sharing"
    ROLLOVER = "rollover"


class RetirementAccount(SQLModel, table=True):
    __tablename__ = "retirement_accounts"
    id: int | None = Field(default=None, primary_key=True)
    account_id: int | None = Field(default=None, foreign_key="accounts.id")
    name: str
    institution: str
    account_type: RetirementAccountType
    annual_contribution_limit: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    catch_up_limit: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(12, 2)))
    employer_match_percent: Decimal | None = Field(default=None, sa_column=Column(Numeric(6, 4), nullable=True))
    employer_match_limit_percent: Decimal | None = Field(default=None, sa_column=Column(Numeric(6, 4), nullable=True))
    current_balance: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(14, 2)))
    is_active: bool = Field(default=True)
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    contributions: list["RetirementContribution"] = Relationship(back_populates="retirement_account")


class RetirementContribution(SQLModel, table=True):
    __tablename__ = "retirement_contributions"
    id: int | None = Field(default=None, primary_key=True)
    retirement_account_id: int = Field(foreign_key="retirement_accounts.id")
    date: date
    employee_contribution: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(12, 2)))
    employer_contribution: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(12, 2)))
    contribution_type: ContributionType
    notes: str | None = None
    retirement_account: RetirementAccount | None = Relationship(back_populates="contributions")

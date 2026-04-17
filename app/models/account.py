from enum import Enum
from datetime import datetime, timezone
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class NormalBalance(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class AccountSubtype(str, Enum):
    # Asset subtypes
    CHECKING = "checking"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    RETIREMENT_ACCOUNT = "retirement_account"
    REAL_ESTATE = "real_estate"
    VEHICLE = "vehicle"
    OTHER_ASSET = "other_asset"
    # Liability subtypes
    CREDIT_CARD = "credit_card"
    MORTGAGE = "mortgage"
    AUTO_LOAN = "auto_loan"
    STUDENT_LOAN = "student_loan"
    OTHER_LIABILITY = "other_liability"
    # Equity subtypes
    RETAINED_EARNINGS = "retained_earnings"
    OPENING_BALANCE = "opening_balance"
    # Revenue subtypes
    SALARY = "salary"
    INVESTMENT_INCOME = "investment_income"
    RENTAL_INCOME = "rental_income"
    OTHER_INCOME = "other_income"
    # Expense subtypes
    HOUSING = "housing"
    FOOD = "food"
    TRANSPORTATION = "transportation"
    HEALTHCARE = "healthcare"
    INSURANCE = "insurance"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    TAX_EXPENSE = "tax_expense"
    OTHER_EXPENSE = "other_expense"


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    account_type: AccountType
    account_subtype: AccountSubtype
    description: Optional[str] = None
    currency: str = Field(default="USD")
    is_active: bool = Field(default=True)
    normal_balance: NormalBalance
    parent_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

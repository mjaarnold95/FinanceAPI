from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.retirement import RetirementAccountType, ContributionType


class RetirementAccountCreate(BaseModel):
    account_id: Optional[int] = None
    name: str
    institution: str
    account_type: RetirementAccountType
    annual_contribution_limit: Decimal
    catch_up_limit: Decimal = Decimal("0")
    employer_match_percent: Optional[Decimal] = None
    employer_match_limit_percent: Optional[Decimal] = None
    current_balance: Decimal = Decimal("0")
    notes: Optional[str] = None


class RetirementAccountUpdate(BaseModel):
    name: Optional[str] = None
    institution: Optional[str] = None
    annual_contribution_limit: Optional[Decimal] = None
    catch_up_limit: Optional[Decimal] = None
    employer_match_percent: Optional[Decimal] = None
    employer_match_limit_percent: Optional[Decimal] = None
    current_balance: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class RetirementAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    account_id: Optional[int] = None
    name: str
    institution: str
    account_type: RetirementAccountType
    annual_contribution_limit: Decimal
    catch_up_limit: Decimal
    employer_match_percent: Optional[Decimal] = None
    employer_match_limit_percent: Optional[Decimal] = None
    current_balance: Decimal
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RetirementContributionCreate(BaseModel):
    date: date
    employee_contribution: Decimal = Decimal("0")
    employer_contribution: Decimal = Decimal("0")
    contribution_type: ContributionType
    notes: Optional[str] = None


class RetirementContributionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    retirement_account_id: int
    date: date
    employee_contribution: Decimal
    employer_contribution: Decimal
    contribution_type: ContributionType
    notes: Optional[str] = None


class YTDContributionSummary(BaseModel):
    year: int
    account_id: int
    account_name: str
    total_employee_contributions: Decimal
    total_employer_contributions: Decimal
    total_contributions: Decimal
    annual_limit: Decimal
    remaining_limit: Decimal


class RetirementProjectionRequest(BaseModel):
    years: int
    annual_return_rate: Decimal  # e.g. 0.07 for 7%
    additional_annual_contribution: Decimal = Decimal("0")


class RetirementProjectionResponse(BaseModel):
    account_id: int
    account_name: str
    current_balance: Decimal
    years: int
    annual_return_rate: Decimal
    additional_annual_contribution: Decimal
    projected_balance: Decimal
    total_contributions: Decimal
    total_growth: Decimal

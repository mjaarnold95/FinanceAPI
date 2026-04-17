from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.account import AccountType, AccountSubtype, NormalBalance


class AccountCreate(BaseModel):
    name: str
    account_type: AccountType
    account_subtype: AccountSubtype
    description: Optional[str] = None
    currency: str = "USD"
    normal_balance: NormalBalance
    parent_id: Optional[int] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    account_type: AccountType
    account_subtype: AccountSubtype
    description: Optional[str] = None
    currency: str
    is_active: bool
    normal_balance: NormalBalance
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class AccountSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    account_type: AccountType
    account_subtype: AccountSubtype
    is_active: bool
    normal_balance: NormalBalance


class AccountBalanceRead(BaseModel):
    account_id: int
    account_name: str
    normal_balance: NormalBalance
    balance: float

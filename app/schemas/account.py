from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.account import AccountType, AccountSubtype, NormalBalance


class AccountCreate(BaseModel):
    name: str
    account_type: AccountType
    account_subtype: AccountSubtype
    description: str | None = None
    currency: str = "USD"
    normal_balance: NormalBalance
    parent_id: int | None = None


class AccountUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    currency: str | None = None
    is_active: bool | None = None
    parent_id: int | None = None


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    account_type: AccountType
    account_subtype: AccountSubtype
    description: str | None = None
    currency: str
    is_active: bool
    normal_balance: NormalBalance
    parent_id: int | None = None
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

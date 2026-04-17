from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.journal_entry import JournalEntryStatus


class JournalEntryLineCreate(BaseModel):
    account_id: int
    debit_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    description: Optional[str] = None


class JournalEntryLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    journal_entry_id: int
    account_id: int
    debit_amount: Decimal
    credit_amount: Decimal
    description: Optional[str] = None


class JournalEntryCreate(BaseModel):
    date: date
    description: str
    reference: Optional[str] = None
    notes: Optional[str] = None
    lines: list[JournalEntryLineCreate]


class JournalEntryUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None


class JournalEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    description: str
    reference: Optional[str] = None
    status: JournalEntryStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    lines: list[JournalEntryLineRead] = []

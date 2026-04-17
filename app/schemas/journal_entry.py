from __future__ import annotations
import datetime as _dt
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.models.journal_entry import JournalEntryStatus


class JournalEntryLineCreate(BaseModel):
    account_id: int
    debit_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    description: str | None = None


class JournalEntryLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    journal_entry_id: int
    account_id: int
    debit_amount: Decimal
    credit_amount: Decimal
    description: str | None = None


class JournalEntryCreate(BaseModel):
    date: _dt.date
    description: str
    reference: str | None = None
    notes: str | None = None
    lines: list[JournalEntryLineCreate]


class JournalEntryUpdate(BaseModel):
    date: _dt.date | None = None
    description: str | None = None
    reference: str | None = None
    notes: str | None = None


class JournalEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: _dt.date
    description: str
    reference: str | None = None
    status: JournalEntryStatus
    notes: str | None = None
    created_at: _dt.datetime
    updated_at: _dt.datetime
    lines: list[JournalEntryLineRead] = []

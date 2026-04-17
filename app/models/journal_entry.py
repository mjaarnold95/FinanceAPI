from enum import StrEnum
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Numeric, Column
from sqlmodel import SQLModel, Field, Relationship


class JournalEntryStatus(StrEnum):
    DRAFT = "draft"
    POSTED = "posted"
    VOIDED = "voided"


class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entries"
    id: int | None = Field(default=None, primary_key=True)
    date: date
    description: str
    reference: str | None = None
    status: JournalEntryStatus = Field(default=JournalEntryStatus.DRAFT)
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lines: list["JournalEntryLine"] = Relationship(back_populates="journal_entry")


class JournalEntryLine(SQLModel, table=True):
    __tablename__ = "journal_entry_lines"
    id: int | None = Field(default=None, primary_key=True)
    journal_entry_id: int = Field(foreign_key="journal_entries.id")
    account_id: int = Field(foreign_key="accounts.id")
    debit_amount: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(12, 2)))
    credit_amount: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(12, 2)))
    description: str | None = None
    journal_entry: JournalEntry | None = Relationship(back_populates="lines")

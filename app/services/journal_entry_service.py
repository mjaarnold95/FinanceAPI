from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.journal_entry import JournalEntry, JournalEntryLine, JournalEntryStatus
from app.schemas.journal_entry import JournalEntryCreate, JournalEntryUpdate


def create_journal_entry(data: JournalEntryCreate, session: Session) -> JournalEntry:
    entry = JournalEntry(
        date=data.date,
        description=data.description,
        reference=data.reference,
        notes=data.notes,
    )
    session.add(entry)
    session.flush()
    for line_data in data.lines:
        line = JournalEntryLine(
            journal_entry_id=entry.id,
            account_id=line_data.account_id,
            debit_amount=line_data.debit_amount,
            credit_amount=line_data.credit_amount,
            description=line_data.description,
        )
        session.add(line)
    session.commit()
    session.refresh(entry)
    return entry


def get_journal_entry(entry_id: int, session: Session) -> Optional[JournalEntry]:
    return session.get(JournalEntry, entry_id)


def get_journal_entries(
    session: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[JournalEntryStatus] = None,
) -> list[JournalEntry]:
    stmt = select(JournalEntry)
    if start_date:
        stmt = stmt.where(JournalEntry.date >= start_date)
    if end_date:
        stmt = stmt.where(JournalEntry.date <= end_date)
    if status:
        stmt = stmt.where(JournalEntry.status == status)
    return list(session.exec(stmt).all())


def post_journal_entry(entry_id: int, session: Session) -> JournalEntry:
    entry = session.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if entry.status != JournalEntryStatus.DRAFT:
        raise HTTPException(status_code=400, detail=f"Cannot post entry with status: {entry.status}")
    total_debits = sum(Decimal(str(line.debit_amount)) for line in entry.lines)
    total_credits = sum(Decimal(str(line.credit_amount)) for line in entry.lines)
    if total_debits != total_credits:
        raise HTTPException(
            status_code=400,
            detail=f"Debits ({total_debits}) must equal credits ({total_credits})"
        )
    entry.status = JournalEntryStatus.POSTED
    entry.updated_at = datetime.utcnow()
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def void_journal_entry(entry_id: int, session: Session) -> JournalEntry:
    entry = session.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if entry.status == JournalEntryStatus.VOIDED:
        raise HTTPException(status_code=400, detail="Entry is already voided")
    entry.status = JournalEntryStatus.VOIDED
    entry.updated_at = datetime.utcnow()
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def get_account_ledger(account_id: int, session: Session) -> list[JournalEntryLine]:
    stmt = select(JournalEntryLine).where(JournalEntryLine.account_id == account_id)
    return list(session.exec(stmt).all())

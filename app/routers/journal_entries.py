from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models.journal_entry import JournalEntryStatus
from app.schemas.journal_entry import JournalEntryCreate, JournalEntryRead, JournalEntryLineRead
from app.services import journal_entry_service

router = APIRouter()


@router.post("/journal-entries", response_model=JournalEntryRead, status_code=201)
def create_journal_entry(data: JournalEntryCreate, session: Session = Depends(get_session)):
    return journal_entry_service.create_journal_entry(data, session)


@router.get("/journal-entries", response_model=list[JournalEntryRead])
def list_journal_entries(
    start_date: date | None = None,
    end_date: date | None = None,
    status: JournalEntryStatus | None = None,
    session: Session = Depends(get_session),
):
    return journal_entry_service.get_journal_entries(session, start_date, end_date, status)


@router.get("/journal-entries/{entry_id}", response_model=JournalEntryRead)
def get_journal_entry(entry_id: int, session: Session = Depends(get_session)):
    entry = journal_entry_service.get_journal_entry(entry_id, session)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry


@router.post("/journal-entries/{entry_id}/post", response_model=JournalEntryRead)
def post_journal_entry(entry_id: int, session: Session = Depends(get_session)):
    return journal_entry_service.post_journal_entry(entry_id, session)


@router.post("/journal-entries/{entry_id}/void", response_model=JournalEntryRead)
def void_journal_entry(entry_id: int, session: Session = Depends(get_session)):
    return journal_entry_service.void_journal_entry(entry_id, session)


@router.get("/accounts/{account_id}/ledger", response_model=list[JournalEntryLineRead])
def get_account_ledger(account_id: int, session: Session = Depends(get_session)):
    return journal_entry_service.get_account_ledger(account_id, session)

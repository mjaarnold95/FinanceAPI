from __future__ import annotations
from decimal import Decimal
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models.account import Account, AccountType
from app.models.journal_entry import JournalEntryLine, JournalEntryStatus, JournalEntry
from app.schemas.account import AccountCreate, AccountUpdate


def create_account(data: AccountCreate, session: Session) -> Account:
    account = Account(**data.model_dump())
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def get_account(account_id: int, session: Session) -> Account | None:
    return session.get(Account, account_id)


def get_accounts(
    session: Session,
    account_type: AccountType | None = None,
    active_only: bool = True,
) -> list[Account]:
    stmt = select(Account)
    if account_type:
        stmt = stmt.where(Account.account_type == account_type)
    if active_only:
        stmt = stmt.where(Account.is_active == True)
    return list(session.exec(stmt).all())


def update_account(account_id: int, data: AccountUpdate, session: Session) -> Account | None:
    account = session.get(Account, account_id)
    if not account:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
    account.updated_at = datetime.now(timezone.utc)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def deactivate_account(account_id: int, session: Session) -> Account | None:
    account = session.get(Account, account_id)
    if not account:
        return None
    account.is_active = False
    account.updated_at = datetime.now(timezone.utc)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def get_account_balance(account_id: int, session: Session) -> Decimal | None:
    account = session.get(Account, account_id)
    if not account:
        return None
    stmt = (
        select(JournalEntryLine)
        .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
        .where(JournalEntryLine.account_id == account_id)
        .where(JournalEntry.status == JournalEntryStatus.POSTED)
    )
    lines = session.exec(stmt).all()
    total_debits = sum(line.debit_amount for line in lines)
    total_credits = sum(line.credit_amount for line in lines)
    if account.normal_balance.value == "debit":
        return Decimal(str(total_debits)) - Decimal(str(total_credits))
    else:
        return Decimal(str(total_credits)) - Decimal(str(total_debits))

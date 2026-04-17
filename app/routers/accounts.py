from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models.account import AccountType
from app.schemas.account import AccountCreate, AccountUpdate, AccountRead, AccountSummary, AccountBalanceRead
from app.services import account_service

router = APIRouter()


@router.post("/accounts", response_model=AccountRead, status_code=201)
def create_account(data: AccountCreate, session: Session = Depends(get_session)):
    return account_service.create_account(data, session)


@router.get("/accounts", response_model=list[AccountSummary])
def list_accounts(
    account_type: Optional[AccountType] = None,
    active_only: bool = True,
    session: Session = Depends(get_session),
):
    return account_service.get_accounts(session, account_type, active_only)


@router.get("/accounts/{account_id}", response_model=AccountRead)
def get_account(account_id: int, session: Session = Depends(get_session)):
    account = account_service.get_account(account_id, session)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch("/accounts/{account_id}", response_model=AccountRead)
def update_account(account_id: int, data: AccountUpdate, session: Session = Depends(get_session)):
    account = account_service.update_account(account_id, data, session)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.delete("/accounts/{account_id}", response_model=AccountRead)
def deactivate_account(account_id: int, session: Session = Depends(get_session)):
    account = account_service.deactivate_account(account_id, session)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.get("/accounts/{account_id}/balance", response_model=AccountBalanceRead)
def get_account_balance(account_id: int, session: Session = Depends(get_session)):
    account = account_service.get_account(account_id, session)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    balance = account_service.get_account_balance(account_id, session)
    return AccountBalanceRead(
        account_id=account_id,
        account_name=account.name,
        normal_balance=account.normal_balance,
        balance=float(balance),
    )

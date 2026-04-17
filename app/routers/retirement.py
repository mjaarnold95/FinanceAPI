from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.schemas.retirement import (
    RetirementAccountCreate, RetirementAccountRead, RetirementAccountUpdate,
    RetirementContributionCreate, RetirementContributionRead,
    YTDContributionSummary, RetirementProjectionRequest, RetirementProjectionResponse
)
from app.services import retirement_service

router = APIRouter()


@router.post("/retirement-accounts", response_model=RetirementAccountRead, status_code=201)
def create_retirement_account(data: RetirementAccountCreate, session: Session = Depends(get_session)):
    return retirement_service.create_retirement_account(data, session)


@router.get("/retirement-accounts", response_model=list[RetirementAccountRead])
def list_retirement_accounts(session: Session = Depends(get_session)):
    return retirement_service.get_retirement_accounts(session)


@router.get("/retirement-accounts/{account_id}", response_model=RetirementAccountRead)
def get_retirement_account(account_id: int, session: Session = Depends(get_session)):
    account = retirement_service.get_retirement_account(account_id, session)
    if not account:
        raise HTTPException(status_code=404, detail="Retirement account not found")
    return account


@router.patch("/retirement-accounts/{account_id}", response_model=RetirementAccountRead)
def update_retirement_account(account_id: int, data: RetirementAccountUpdate, session: Session = Depends(get_session)):
    account = retirement_service.update_retirement_account(account_id, data, session)
    if not account:
        raise HTTPException(status_code=404, detail="Retirement account not found")
    return account


@router.post("/retirement-accounts/{account_id}/contributions", response_model=RetirementContributionRead, status_code=201)
def add_contribution(account_id: int, data: RetirementContributionCreate, session: Session = Depends(get_session)):
    return retirement_service.add_contribution(account_id, data, session)


@router.get("/retirement-accounts/{account_id}/contributions", response_model=list[RetirementContributionRead])
def list_contributions(account_id: int, session: Session = Depends(get_session)):
    return retirement_service.get_contributions_for_account(account_id, session)


@router.get("/retirement-accounts/{account_id}/ytd", response_model=YTDContributionSummary)
def get_ytd_contributions(account_id: int, year: int = Query(...), session: Session = Depends(get_session)):
    return retirement_service.calculate_ytd_contributions(account_id, year, session)


@router.post("/retirement-accounts/{account_id}/projection", response_model=RetirementProjectionResponse)
def project_retirement_balance(account_id: int, data: RetirementProjectionRequest, session: Session = Depends(get_session)):
    return retirement_service.project_retirement_balance(account_id, data, session)

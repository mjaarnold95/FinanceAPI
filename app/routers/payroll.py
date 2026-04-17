from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.payroll import PayPeriodCreate, PayPeriodRead, PayStubCreate, PayStubRead, YTDSummary
from app.services import payroll_service

router = APIRouter()


@router.post("/pay-periods", response_model=PayPeriodRead, status_code=201)
def create_pay_period(data: PayPeriodCreate, session: Session = Depends(get_session)):
    return payroll_service.create_pay_period(data, session)


@router.get("/pay-periods", response_model=list[PayPeriodRead])
def list_pay_periods(session: Session = Depends(get_session)):
    return payroll_service.get_pay_periods(session)


@router.get("/pay-periods/{period_id}", response_model=PayPeriodRead)
def get_pay_period(period_id: int, session: Session = Depends(get_session)):
    period = payroll_service.get_pay_period(period_id, session)
    if not period:
        raise HTTPException(status_code=404, detail="Pay period not found")
    return period


@router.post("/pay-periods/{period_id}/pay-stubs", response_model=PayStubRead, status_code=201)
def create_pay_stub(period_id: int, data: PayStubCreate, session: Session = Depends(get_session)):
    period = payroll_service.get_pay_period(period_id, session)
    if not period:
        raise HTTPException(status_code=404, detail="Pay period not found")
    return payroll_service.create_pay_stub(period_id, data, session)


@router.get("/pay-periods/{period_id}/pay-stubs", response_model=list[PayStubRead])
def list_pay_stubs(period_id: int, session: Session = Depends(get_session)):
    return payroll_service.get_pay_stubs_for_period(period_id, session)


@router.get("/payroll/ytd-summary", response_model=YTDSummary)
def get_ytd_summary(year: int, session: Session = Depends(get_session)):
    return payroll_service.get_ytd_summary(year, session)

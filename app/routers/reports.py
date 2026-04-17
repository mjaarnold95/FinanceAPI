from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.database import get_session
from app.services import report_service

router = APIRouter()


@router.get("/reports/income-statement")
def get_income_statement(
    start_date: date = Query(...),
    end_date: date = Query(...),
    session: Session = Depends(get_session),
):
    return report_service.get_income_statement(start_date, end_date, session)


@router.get("/reports/balance-sheet")
def get_balance_sheet(
    as_of_date: date = Query(...),
    session: Session = Depends(get_session),
):
    return report_service.get_balance_sheet(as_of_date, session)


@router.get("/reports/cash-flow")
def get_cash_flow(
    start_date: date = Query(...),
    end_date: date = Query(...),
    session: Session = Depends(get_session),
):
    return report_service.get_cash_flow_statement(start_date, end_date, session)


@router.get("/reports/net-worth")
def get_net_worth(session: Session = Depends(get_session)):
    return report_service.get_net_worth(session)

from decimal import Decimal
from datetime import date
from typing import Optional
from sqlmodel import Session, select
from app.models.account import Account, AccountType, AccountSubtype
from app.models.journal_entry import JournalEntry, JournalEntryLine, JournalEntryStatus


def _get_account_balances(
    session: Session,
    account_types: list[AccountType],
    as_of_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> dict[int, Decimal]:
    """Compute balance for each account of the given types."""
    stmt = (
        select(JournalEntryLine, Account)
        .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalEntryLine.account_id == Account.id)
        .where(JournalEntry.status == JournalEntryStatus.POSTED)
        .where(Account.account_type.in_(account_types))
    )
    if as_of_date:
        stmt = stmt.where(JournalEntry.date <= as_of_date)
    if start_date:
        stmt = stmt.where(JournalEntry.date >= start_date)
    if end_date:
        stmt = stmt.where(JournalEntry.date <= end_date)
    results = session.exec(stmt).all()
    balances: dict[int, Decimal] = {}
    for line, account in results:
        aid = account.id
        if aid not in balances:
            balances[aid] = Decimal("0")
        debit = Decimal(str(line.debit_amount))
        credit = Decimal(str(line.credit_amount))
        if account.normal_balance.value == "debit":
            balances[aid] += debit - credit
        else:
            balances[aid] += credit - debit
    return balances


def get_income_statement(start_date: date, end_date: date, session: Session) -> dict:
    revenue_balances = _get_account_balances(session, [AccountType.REVENUE], start_date=start_date, end_date=end_date)
    expense_balances = _get_account_balances(session, [AccountType.EXPENSE], start_date=start_date, end_date=end_date)
    total_revenue = sum(revenue_balances.values()) if revenue_balances else Decimal("0")
    total_expenses = sum(expense_balances.values()) if expense_balances else Decimal("0")
    revenue_accounts = []
    for aid, bal in revenue_balances.items():
        account = session.get(Account, aid)
        if account:
            revenue_accounts.append({"account_id": aid, "account_name": account.name, "amount": float(bal)})
    expense_accounts = []
    for aid, bal in expense_balances.items():
        account = session.get(Account, aid)
        if account:
            expense_accounts.append({"account_id": aid, "account_name": account.name, "amount": float(bal)})
    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "revenue": revenue_accounts,
        "total_revenue": float(total_revenue),
        "expenses": expense_accounts,
        "total_expenses": float(total_expenses),
        "net_income": float(total_revenue - total_expenses),
    }


def get_balance_sheet(as_of_date: date, session: Session) -> dict:
    asset_balances = _get_account_balances(session, [AccountType.ASSET], as_of_date=as_of_date)
    liability_balances = _get_account_balances(session, [AccountType.LIABILITY], as_of_date=as_of_date)
    equity_balances = _get_account_balances(session, [AccountType.EQUITY], as_of_date=as_of_date)
    total_assets = sum(asset_balances.values()) if asset_balances else Decimal("0")
    total_liabilities = sum(liability_balances.values()) if liability_balances else Decimal("0")
    total_equity = sum(equity_balances.values()) if equity_balances else Decimal("0")

    def build_list(balances: dict[int, Decimal]) -> list[dict]:
        result = []
        for aid, bal in balances.items():
            account = session.get(Account, aid)
            if account:
                result.append({"account_id": aid, "account_name": account.name, "amount": float(bal)})
        return result

    return {
        "as_of_date": str(as_of_date),
        "assets": build_list(asset_balances),
        "total_assets": float(total_assets),
        "liabilities": build_list(liability_balances),
        "total_liabilities": float(total_liabilities),
        "equity": build_list(equity_balances),
        "total_equity": float(total_equity),
        "total_liabilities_and_equity": float(total_liabilities + total_equity),
    }


def get_cash_flow_statement(start_date: date, end_date: date, session: Session) -> dict:
    stmt = (
        select(Account)
        .where(Account.account_type == AccountType.ASSET)
        .where(Account.account_subtype.in_([AccountSubtype.CHECKING, AccountSubtype.SAVINGS]))
    )
    cash_accounts = list(session.exec(stmt).all())
    cash_account_ids = {a.id for a in cash_accounts}
    stmt2 = (
        select(JournalEntryLine, JournalEntry)
        .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
        .where(JournalEntry.status == JournalEntryStatus.POSTED)
        .where(JournalEntry.date >= start_date)
        .where(JournalEntry.date <= end_date)
        .where(JournalEntryLine.account_id.in_(cash_account_ids))
    )
    results = list(session.exec(stmt2).all())
    cash_inflows = Decimal("0")
    cash_outflows = Decimal("0")
    for line, entry in results:
        debit = Decimal(str(line.debit_amount))
        credit = Decimal(str(line.credit_amount))
        # For asset (debit normal): debit = inflow, credit = outflow
        cash_inflows += debit
        cash_outflows += credit
    net_cash_flow = cash_inflows - cash_outflows
    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "cash_inflows": float(cash_inflows),
        "cash_outflows": float(cash_outflows),
        "net_cash_flow": float(net_cash_flow),
    }


def get_net_worth(session: Session) -> dict:
    today = date.today()
    asset_balances = _get_account_balances(session, [AccountType.ASSET], as_of_date=today)
    liability_balances = _get_account_balances(session, [AccountType.LIABILITY], as_of_date=today)
    total_assets = sum(asset_balances.values()) if asset_balances else Decimal("0")
    total_liabilities = sum(liability_balances.values()) if liability_balances else Decimal("0")
    return {
        "as_of_date": str(today),
        "total_assets": float(total_assets),
        "total_liabilities": float(total_liabilities),
        "net_worth": float(total_assets - total_liabilities),
    }

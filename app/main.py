from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import accounts, journal_entries, payroll, tax, retirement, reports
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    description="A robust personal finance monitoring API with double-entry accounting",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(accounts.router, prefix="/api/v1", tags=["Accounts"])
app.include_router(journal_entries.router, prefix="/api/v1", tags=["Journal Entries"])
app.include_router(payroll.router, prefix="/api/v1", tags=["Payroll"])
app.include_router(tax.router, prefix="/api/v1", tags=["Tax Planning"])
app.include_router(retirement.router, prefix="/api/v1", tags=["Retirement"])
app.include_router(reports.router, prefix="/api/v1", tags=["Financial Reports"])


@app.get("/")
def root():
    return {"message": "Welcome to FinanceAPI", "docs": "/docs"}

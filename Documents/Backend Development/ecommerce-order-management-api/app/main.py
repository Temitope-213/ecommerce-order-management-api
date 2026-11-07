import logging

import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import admin, auth
from app.domain.exceptions import EmailAlreadyExistsError, InvalidCredentialsError

logger = logging.getLogger(__name__)

app = FastAPI(title="E-Commerce & Order Management API")
app.include_router(auth.router)
app.include_router(admin.router)


@app.exception_handler(EmailAlreadyExistsError)
async def email_exists(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=409, content={"detail": "Email is already registered"}
    )


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Incorrect email or password"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(psycopg.OperationalError)
async def db_connection_error(request: Request, exc: psycopg.OperationalError):
    logger.error("Database connection error")
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.exception_handler(psycopg.Error)
async def db_error(request: Request, exc: psycopg.Error):
    logger.error("Database error: %s", type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
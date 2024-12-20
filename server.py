# encoding: utf-8
import logging
import os
from typing import Optional

import fastapi.logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy import text

from dbsession import async_session
from helper.LimitUploadSize import LimitUploadSize
from cryptixd.CryptixdMultiClient import CryptixdMultiClient

fastapi.logger.logger.setLevel(logging.WARNING)
_logger = logging.getLogger(__name__)

# FastAPI-Anwendung erstellen
app = FastAPI(
    title="Cryptix REST-API server",
    description="This server is to communicate with Cryptix Network via REST-API",
    version=os.getenv("VERSION", "tbd"),
    contact={"name": "Cryptix Network"},
    license_info={"name": "MIT LICENSE"},
)

# Middleware hinzufügen
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(LimitUploadSize, max_upload_size=200_000)  # ~1MB

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models für die Antwort
class CryptixdStatus(BaseModel):
    is_online: bool = False
    server_version: Optional[str] = None
    is_utxo_indexed: Optional[bool] = None
    is_synced: Optional[bool] = None


class DatabaseStatus(BaseModel):
    is_online: bool = False


class PingResponse(BaseModel):
    cryptixd: CryptixdStatus = CryptixdStatus()
    database: DatabaseStatus = DatabaseStatus()


@app.get("/ping", include_in_schema=False, response_model=PingResponse)
async def ping_server():
    """
    Ping Pong - Überprüft den Status von Cryptixd und der Datenbank
    """
    result = PingResponse()
    error = False

    # Überprüfung der Cryptixd-Client-Verbindung
    try:
        info = await cryptixd_client.cryptixds[0].request("getInfoRequest")
        result.cryptixd.is_online = True
        result.cryptixd.server_version = info["getInfoResponse"]["serverVersion"]
        result.cryptixd.is_utxo_indexed = info["getInfoResponse"]["isUtxoIndexed"]
        result.cryptixd.is_synced = info["getInfoResponse"]["isSynced"]
    except Exception as err:
        _logger.error("Cryptixd health check failed: %s", err)
        error = True

    # Überprüfung der Datenbankverbindung
    if os.getenv("SQL_URI") is not None:
        async with async_session() as session:
            try:
                # SQL-Abfrage korrekt ausführen mit text()
                await session.execute(text("SELECT 1"))
                result.database.is_online = True
            except Exception as err:
                _logger.error("Database health check failed: %s", err)
                error = True

    # Wenn ein Fehler aufgetreten ist oder Cryptixd nicht synchronisiert ist
    if error or not result.cryptixd.is_synced:
        return JSONResponse(status_code=500, content=result.dict())

    return result


# Einrichten der Cryptixd-Hosts
cryptixd_hosts = []

# Versuche, bis zu 100 Cryptixd-Hosts zu laden
for i in range(100):
    try:
        cryptixd_hosts.append(os.environ[f"CRYPTIXD_HOST_{i + 1}"].strip())
    except KeyError:
        break

# Wenn keine Hosts gesetzt sind, wird eine Ausnahme geworfen
if not cryptixd_hosts:
    raise Exception("Please set at least CRYPTIXD_HOST_1 environment variable.")

# CryptixdClient initialisieren
cryptixd_client = CryptixdMultiClient(cryptixd_hosts)


# Ausnahmebehandlung für alle unerwarteten Fehler
@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    await cryptixd_client.initialize_all()
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error"
            # Optional: "traceback": f"{traceback.format_exception(exc)}"
        },
    )


# Periodische Initialisierung des Clients bei Server-Start
@app.on_event("startup")
@repeat_every(seconds=60)
async def periodical_blockdag():
    await cryptixd_client.initialize_all()

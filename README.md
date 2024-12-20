#Cryptix Rest Server

Start with a Bat File / Powershell file or similar:

## Powershell:


if (-not (Test-Path -Path .\venv)) {
    python -m venv venv
}


. .\venv\Scripts\Activate


$env:PYTHONPATH = "$env:PYTHONPATH;C:\your-path\cryptix-rest-server\cryptixd"
$env:CRYPTIXD_HOST_1 = "127.0.0.1:19201"
$env:SQL_URI = "postgresql+asyncpg://postgres:yourpass@localhost:5432/postgres"
$env:VERSION = "$Version"


uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir C:\your-path\cryptix-rest-server


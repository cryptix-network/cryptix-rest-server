# encoding: utf-8
import os

from fastapi import Path, HTTPException
from pydantic import BaseModel

from server import app, cryptixd_client

CRYPTIX_ADDRESS_PREFIX = os.getenv("ADDRESS_PREFIX", "cryptix")


class BalanceResponse(BaseModel):
    address: str = (
        CRYPTIX_ADDRESS_PREFIX
        + ":pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00"
    )
    balance: int = 38240000000


@app.get(
    "/addresses/{cryptixAddress}/balance",
    response_model=BalanceResponse,
    tags=["Cryptix addresses"],
)
async def get_balance_from_cryptix_address(
    cryptixAddress: str = Path(
        description="Cryptix address as string e.g. "
        + CRYPTIX_ADDRESS_PREFIX
        + ":pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
        regex=r"^" + CRYPTIX_ADDRESS_PREFIX + r"\:[a-z0-9]{61,63}$",
    ),
):
    """
    Get the balance for a specified Cryptix address.
    """
    resp = await cryptixd_client.request(
        "getBalanceByAddressRequest", params={"address": cryptixAddress}
    )

    try:
        resp = resp["getBalanceByAddressResponse"]
    except KeyError:
        if (
            "getUtxosByAddressesResponse" in resp
            and "error" in resp["getUtxosByAddressesResponse"]
        ):
            raise HTTPException(
                status_code=400, detail=resp["getUtxosByAddressesResponse"]["error"]
            )
        else:
            raise

    try:
        balance = int(resp["balance"])

    # return 0 if address is ok, but no utxos there
    except KeyError:
        balance = 0

    return {"address": cryptixAddress, "balance": balance}

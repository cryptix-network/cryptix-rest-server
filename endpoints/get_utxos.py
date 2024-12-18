# encoding: utf-8
import os

from typing import List

from fastapi import Path, HTTPException
from pydantic import BaseModel

from server import app, cryptixd_client

CRYPTIX_ADDRESS_PREFIX = os.getenv("ADDRESS_PREFIX", "cryptix")


class OutpointModel(BaseModel):
    transactionId: str = (
        "ef62efbc2825d3ef9ec1cf9b80506876ac077b64b11a39c8ef5e028415444dc9"
    )
    index: int = 0


class ScriptPublicKeyModel(BaseModel):
    scriptPublicKey: str = (
        "20c5629ce85f6618cd3ed1ac1c99dc6d3064ed244013555c51385d9efab0d0072fac"
    )


class UtxoModel(BaseModel):
    amount: str = ("11501593788",)
    scriptPublicKey: ScriptPublicKeyModel
    blockDaaScore: str = "18867232"
    isCoinbase: bool = False


class UtxoResponse(BaseModel):
    address: str = (
        CRYPTIX_ADDRESS_PREFIX
        + ":qrzk988gtanp3nf76xkpexwud5cxfmfygqf42hz38pwea74s6qrj75jee85nj"
    )
    outpoint: OutpointModel
    utxoEntry: UtxoModel


@app.get(
    "/addresses/{cryptixAddress}/utxos",
    response_model=List[UtxoResponse],
    tags=["Cryptix addresses"],
)
async def get_utxos_for_address(
    cryptixAddress: str = Path(
        description="Cryptix address as string e.g. "
        + CRYPTIX_ADDRESS_PREFIX
        + ":qqkqkzjvr7zwxxmjxjkmxxdwju9kjs6e9u82uh59z07vgaks6gg62v8707g73",
        regex=r"^" + CRYPTIX_ADDRESS_PREFIX + r"\:[a-z0-9]{61,63}$",
    ),
):
    """
    List all unspent transaction outputs (UTXOs) for the specified Cryptix address.
    """
    resp = await cryptixd_client.request(
        "getUtxosByAddressesRequest",
        params={"addresses": [cryptixAddress]},
        timeout=120,
    )
    try:
        return (
            utxo
            for utxo in resp["getUtxosByAddressesResponse"]["entries"]
            if utxo["address"] == cryptixAddress
        )
    except KeyError:
        if (
            "getUtxosByAddressesResponse" in resp
            and "error" in resp["getUtxosByAddressesResponse"]
        ):
            raise HTTPException(
                status_code=400, detail=resp["getUtxosByAddressesResponse"]["error"]
            )
        else:
            return []

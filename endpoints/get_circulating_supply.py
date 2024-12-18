# encoding: utf-8

from pydantic import BaseModel

from server import app, cryptixd_client
from fastapi.responses import PlainTextResponse


class CoinSupplyResponse(BaseModel):
    circulatingSupply: str = "19295068591369439"
    maxSupply: str = "116100000000000000"


@app.get(
    "/info/coinsupply", response_model=CoinSupplyResponse, tags=["Cryptix network info"]
)
async def get_coinsupply():
    """
    Get $CYTX coin supply information.
    """
    resp = await cryptixd_client.request("getCoinSupplyRequest")
    return {
        "circulatingSupply": resp["getCoinSupplyResponse"]["circulatingSompi"],
        "totalSupply": resp["getCoinSupplyResponse"]["circulatingSompi"],
        "maxSupply": resp["getCoinSupplyResponse"]["maxSompi"],
    }


@app.get(
    "/info/coinsupply/circulating",
    tags=["Cryptix network info"],
    response_class=PlainTextResponse,
)
async def get_circulating_coins(in_billion: bool = False):
    """
    Get circulating amount of $CYTX coin as numerical value.
    """
    resp = await cryptixd_client.request("getCoinSupplyRequest")
    coins = str(float(resp["getCoinSupplyResponse"]["circulatingSompi"]) / 1e8)
    if in_billion:
        return str(round(float(coins) / 1e9, 2))
    else:
        return coins


@app.get(
    "/info/coinsupply/total",
    tags=["Cryptix network info"],
    response_class=PlainTextResponse,
)
async def get_total_coins():
    """
    Get total amount of $CYTX coin as numerical value.
    """
    resp = await cryptixd_client.request("getCoinSupplyRequest")
    return str(float(resp["getCoinSupplyResponse"]["circulatingSompi"]) / 1e8)


@app.get(
    "/info/coinsupply/max",
    tags=["Cryptix network info"],
    response_class=PlainTextResponse,
)
async def get_max_coins():
    """
    Get maximum amount of $CYTX coin as numerical value.
    """
    resp = await cryptixd_client.request("getCoinSupplyRequest")
    return str(float(resp["getCoinSupplyResponse"]["maxSompi"]) / 1e8)

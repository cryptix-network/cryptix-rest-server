# encoding: utf-8

from pydantic import BaseModel

from helper import get_cytx_price
from server import app, cryptixd_client


class MarketCapResponse(BaseModel):
    marketcap: int = 12000132


@app.get(
    "/info/marketcap",
    response_model=MarketCapResponse | str,
    tags=["Cryptix network info"],
)
async def get_marketcap(stringOnly: bool = False):
    """
    Get $CYTX price and market cap. Price info is from coingecko.com
    """
    cytx_price = await get_cytx_price()
    resp = await cryptixd_client.request("getCoinSupplyRequest")
    mcap = round(
        float(resp["getCoinSupplyResponse"]["circulatingSompi"]) / 1e8 * cytx_price
    )

    if not stringOnly:
        return {"marketcap": mcap}
    else:
        if mcap < 1e9:
            return f"{round(mcap / 1e6, 1)}M"
        else:
            return f"{round(mcap / 1e9, 1)}B"

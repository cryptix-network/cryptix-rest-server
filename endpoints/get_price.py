# encoding: utf-8

from pydantic import BaseModel
from starlette.responses import PlainTextResponse

from helper import get_cytx_price, get_cytx_market_data
from server import app


class PriceResponse(BaseModel):
    price: float = 0.0314


@app.get(
    "/info/price", response_model=PriceResponse | str, tags=["Cryptix network info"]
)
async def get_price(stringOnly: bool = False):
    """
    Returns the current price for Cryptix in USD. Price info is from coingecko.com
    """
    if stringOnly:
        return PlainTextResponse(content=str(await get_cytx_price()))

    return {"price": await get_cytx_price()}


@app.get("/info/market-data", tags=["Cryptix network info"], include_in_schema=False)
async def get_market_data():
    """
    Returns market data for Cryptix.
    """
    return await get_cytx_market_data()

# encoding: utf-8
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel

from server import app, cryptixd_client

current_blue_score_data = {"blue_score": 0}


class BlockdagResponse(BaseModel):
    blueScore: int = 260890


@app.get(
    "/info/virtual-chain-blue-score",
    response_model=BlockdagResponse,
    tags=["Cryptix network info"],
)
async def get_virtual_selected_parent_blue_score():
    """
    Returns the blue score of virtual selected parent.
    """
    resp = await cryptixd_client.request("getSinkBlueScoreRequest")
    return resp["getSinkBlueScoreResponse"]


@app.on_event("startup")
@repeat_every(seconds=5)
async def update_blue_score():
    global current_blue_score_data
    resp = await cryptixd_client.request("getSinkBlueScoreRequest")
    current_blue_score_data["blue_score"] = int(
        resp["getSinkBlueScoreResponse"]["blueScore"]
    )
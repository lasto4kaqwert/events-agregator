from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

router = APIRouter(
    prefix="/sync",
    tags=["sync"],
)


@router.post("/trigger", response_model=BaseModel)
async def run_sync(

) -> BaseModel:
    pass
from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.post("", response_model=BaseModel)
async def create_ticket(
    payload: BaseModel,
) -> BaseModel:
    pass


@router.delete("/{ticket_id}", response_model=BaseModel)
async def delete_ticket(
    ticket_id: int,
) -> BaseModel:
    pass
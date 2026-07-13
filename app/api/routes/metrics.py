from fastapi import APIRouter

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)


@router.get("/metrics")
def metrics():
    return {}
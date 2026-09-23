from fastapi import APIRouter, HTTPException
from ..data_store import LocalStore

router = APIRouter(prefix="/api", tags=["investigation"])
store = LocalStore()

@router.get("/health")
def health():
    return {"status": "ok", "mode": "local"}

@router.get("/cases")
def cases():
    return {"cases": store.case_list()}

@router.get("/cases/{case_id}")
def case(case_id: str):
    x = store.case(case_id)
    if x is None:
        raise HTTPException(404, "Case not found")
    return x

@router.get("/transactions/{transaction_id}")
def transaction(transaction_id: str):
    x = store.transaction(transaction_id)
    if x is None:
        raise HTTPException(404, "Transaction not found")
    return x

@router.get("/customers/{customer_id}/history")
def customer_history(customer_id: str, limit: int = 100):
    return {"customer_id": customer_id, "transactions": store.customer_history(customer_id, limit)}

@router.get("/cards/{card_id}/transactions")
def card_transactions(card_id: str, limit: int = 200):
    return {"card_id": card_id, "transactions": store.card_transactions(card_id, limit)}

@router.get("/devices/{device_id}/transactions")
def device_transactions(device_id: str, limit: int = 200):
    return {"device_profile_id": device_id, "transactions": store.device_neighbors(device_id, limit)}

@router.get("/regions/{region_id}/transactions")
def region_transactions(region_id: str, limit: int = 200):
    return {"region_id": region_id, "transactions": store.region_neighbors(region_id, limit)}

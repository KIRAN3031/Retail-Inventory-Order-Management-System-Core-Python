from typing import Optional, Dict, List
from src.config import get_supabase

class PaymentDAOError(Exception):
    pass

class PaymentDAO:
    def __init__(self):
        self._sb = get_supabase()

    def create_payment(self, order_id: int, amount: float) -> Optional[Dict]:
        payload = {
            "order_id": order_id,
            "amount": amount,
            "status": "PENDING",
            "method": None
        }
        self._sb.table("payments").insert(payload).execute()
        resp = self._sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_payment(self, payment_id: int, status: str, method: Optional[str] = None) -> Optional[Dict]:
        update_fields = {"status": status}
        if method is not None:
            update_fields["method"] = method
        self._sb.table("payments").update(update_fields).eq("payment_id", payment_id).execute()
        resp = self._sb.table("payments").select("*").eq("payment_id", payment_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_payment_by_order(self, order_id: int) -> Optional[Dict]:
        resp = self._sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None
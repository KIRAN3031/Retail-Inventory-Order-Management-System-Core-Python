from typing import Optional, List, Dict
from src.config import get_supabase

class OrderDAOError(Exception):
    pass

class OrderDAO:
    def __init__(self):
        self._sb = get_supabase()

    def create_order(self, customer_id: int, items: List[Dict]) -> Dict:
        # Insert new order with status 'PLACED', total_amount initially 0
        payload = {"customer_id": customer_id, "status": "PLACED", "total_amount": 0}
        self._sb.table("orders").insert(payload).execute()
        resp = self._sb.table("orders").select("*").order("order_id", desc=True).limit(1).execute()
        order = resp.data[0] if resp.data else None
        if not order:
            raise OrderDAOError("Failed to create order")

        order_id = order["order_id"]

        # Insert order_items entries
        total_amount = 0
        for item in items:
            prod_id = item["prod_id"]
            quantity = item["quantity"]
            self._sb.table("order_items").insert({
                "order_id": order_id,
                "product_id": prod_id,
                "quantity": quantity
            }).execute()

            # Fetch product price for calculation
            prod_resp = self._sb.table("products").select("price").eq("product_id", prod_id).limit(1).execute()
            price = prod_resp.data[0]["price"] if prod_resp.data else 0
            total_amount += price * quantity

        # Update order total_amount
        self._sb.table("orders").update({"total_amount": total_amount}).eq("order_id", order_id).execute()
        order["total_amount"] = total_amount

        return order

    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        resp = self._sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def list_orders_by_customer(self, customer_id: int) -> List[Dict]:
        resp = self._sb.table("orders").select("*").eq("customer_id", customer_id).order("order_id").execute()
        return resp.data or []

    def update_order_status(self, order_id: int, status: str) -> Optional[Dict]:
        self._sb.table("orders").update({"status": status}).eq("order_id", order_id).execute()
        resp = self._sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_order_items(self, order_id: int) -> List[Dict]:
        resp = self._sb.table("order_items").select("*").eq("order_id", order_id).execute()
        return resp.data or []

    def delete_order_items(self, order_id: int) -> None:
        self._sb.table("order_items").delete().eq("order_id", order_id).execute()
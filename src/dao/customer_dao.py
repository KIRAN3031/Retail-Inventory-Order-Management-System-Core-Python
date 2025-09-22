from typing import Optional, List, Dict
from src.config import get_supabase

class CustomerDAOError(Exception):
    pass

class CustomerDAO:
    def __init__(self):
        self._sb = get_supabase()

    def create_customer(self, name: str, email: str, phone: Optional[str] = None, city: Optional[str] = None) -> Dict:
        if not name or not email:
            raise CustomerDAOError("Name and email are required")

        existing = self.get_customer_by_email(email)
        if existing:
            raise CustomerDAOError(f"Email already exists: {email}")

        payload = {"name": name, "email": email, "phone": phone, "city": city}

        self._sb.table("customers").insert(payload).execute()
        resp = self._sb.table("customers").select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_customer_by_id(self, cust_id: int) -> Optional[Dict]:
        resp = self._sb.table("customers").select("*").eq("customer_id", cust_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        resp = self._sb.table("customers").select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_customer(self, cust_id: int, fields: Dict) -> Optional[Dict]:
        if not fields:
            raise CustomerDAOError("No fields to update")

        self._sb.table("customers").update(fields).eq("customer_id", cust_id).execute()
        resp = self._sb.table("customers").select("*").eq("customer_id", cust_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def delete_customer(self, cust_id: int) -> Optional[Dict]:
        orders_resp = self._sb.table("orders").select("*").eq("customer_id", cust_id).limit(1).execute()
        if orders_resp.data:
            raise CustomerDAOError("Cannot delete customer with existing orders.")

        resp_before = self._sb.table("customers").select("*").eq("customer_id", cust_id).limit(1).execute()
        row = resp_before.data[0] if resp_before.data else None
        self._sb.table("customers").delete().eq("customer_id", cust_id).execute()
        return row

    def list_customers(self, limit: int = 100) -> List[Dict]:
        resp = self._sb.table("customers").select("*").order("customer_id", desc=False).limit(limit).execute()
        return resp.data or []

    def search_customers(self, email: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
        q = self._sb.table("customers").select("*")
        if email:
            q = q.eq("email", email)
        if city:
            q = q.eq("city", city)
        resp = q.execute()
        return resp.data or []
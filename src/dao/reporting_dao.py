from typing import List, Dict
from datetime import datetime, timedelta
from src.config import get_supabase

class ReportingDAO:
    def __init__(self):
        self._sb = get_supabase()

    def get_top_selling_products(self, top_n: int = 5) -> List[Dict]:
        resp = self._sb.table("order_items")\
            .select("product_id, sum_quantity:sum(quantity)")\
            .group("product_id")\
            .order("sum_quantity", desc=True)\
            .limit(top_n).execute()
        return resp.data or []

    def get_total_revenue_last_month(self) -> float:
        today = datetime.utcnow().date()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)

        resp = self._sb.table("orders")\
            .select("sum_total:sum(total_amount)")\
            .gte("created_at", str(first_day_last_month))\
            .lte("created_at", str(last_day_last_month))\
            .eq("status", "COMPLETED").execute()
        if resp.data and resp.data[0]["sum_total"] is not None:
            return float(resp.data[0]["sum_total"])
        return 0.0

    def get_order_count_per_customer(self) -> List[Dict]:
        resp = self._sb.table("orders")\
            .select("customer_id, order_count:count(order_id)")\
            .group("customer_id").execute()
        return resp.data or []

    def get_customers_with_multiple_orders(self, min_orders: int = 2) -> List[Dict]:
        resp = self._sb.table("orders")\
            .select("customer_id, order_count:count(order_id)")\
            .group("customer_id")\
            .having("order_count", ">", min_orders)\
            .execute()
        return resp.data or []

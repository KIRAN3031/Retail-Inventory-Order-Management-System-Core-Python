from typing import List, Dict
from src.dao.reporting_dao import ReportingDAO

class ReportingService:
    def __init__(self):
        self.dao = ReportingDAO()

    def get_top_selling_products(self, top_n: int = 5) -> List[Dict]:
        return self.dao.get_top_selling_products(top_n)

    def get_total_revenue_last_month(self) -> float:
        return self.dao.get_total_revenue_last_month()

    def get_order_count_per_customer(self) -> List[Dict]:
        return self.dao.get_order_count_per_customer()

    def get_customers_with_multiple_orders(self, min_orders: int = 2) -> List[Dict]:
        return self.dao.get_customers_with_multiple_orders(min_orders)
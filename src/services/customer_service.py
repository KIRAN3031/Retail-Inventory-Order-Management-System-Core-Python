from typing import Optional, List, Dict
from src.dao.customer_dao import CustomerDAO, CustomerDAOError

class CustomerServiceError(Exception):
    pass

class CustomerService:
    def __init__(self):
        self.dao = CustomerDAO()

    def create_customer(self, name: str, email: str, phone: Optional[str] = None, city: Optional[str] = None) -> Dict:
        try:
            return self.dao.create_customer(name, email, phone, city)
        except CustomerDAOError as e:
            raise CustomerServiceError(str(e))

    def get_customer(self, cust_id: int) -> Optional[Dict]:
        return self.dao.get_customer_by_id(cust_id)

    def update_customer(self, cust_id: int, phone: Optional[str] = None, city: Optional[str] = None) -> Optional[Dict]:
        fields = {}
        if phone is not None:
            fields["phone"] = phone
        if city is not None:
            fields["city"] = city
        if not fields:
            raise CustomerServiceError("At least one field (phone or city) must be provided for update")
        try:
            return self.dao.update_customer(cust_id, fields)
        except CustomerDAOError as e:
            raise CustomerServiceError(str(e))

    def delete_customer(self, cust_id: int) -> Optional[Dict]:
        try:
            return self.dao.delete_customer(cust_id)
        except CustomerDAOError as e:
            raise CustomerServiceError(str(e))

    def list_customers(self, limit: int = 100) -> List[Dict]:
        return self.dao.list_customers(limit)

    def search_customers(self, email: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
        return self.dao.search_customers(email, city)
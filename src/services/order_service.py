from typing import List, Dict, Optional
from src.dao.order_dao import OrderDAO, OrderDAOError
from src.dao.product_dao import ProductDAO, ProductDAOError
from src.dao.customer_dao import CustomerDAO, CustomerDAOError

class OrderServiceError(Exception):
    pass

class OrderService:
    def __init__(self):
        self.order_dao = OrderDAO()
        self.product_dao = ProductDAO()
        self.customer_dao = CustomerDAO()

    def create_order(self, customer_id: int, items: List[Dict[str, int]]) -> Dict:
        # Validate customer exists
        cust = self.customer_dao.get_customer_by_id(customer_id)
        if not cust:
            raise OrderServiceError("Customer not found")

        # Validate product stock and calculate total
        for item in items:
            prod_id = item["prod_id"]
            quantity = item["quantity"]
            product = self.product_dao.get_product_by_id(prod_id)
            if not product:
                raise OrderServiceError(f"Product with id {prod_id} not found")
            stock = product.get("stock", 0)
            if stock < quantity:
                raise OrderServiceError(f"Not enough stock for product id {prod_id}")

        # Deduct stock for each product
        for item in items:
            prod_id = item["prod_id"]
            quantity = item["quantity"]
            product = self.product_dao.get_product_by_id(prod_id)
            new_stock = (product.get("stock") or 0) - quantity
            self.product_dao.update_product(prod_id, {"stock": new_stock})

        # Create order and order_items records
        order = self.order_dao.create_order(customer_id, items)
        return order

    def get_order_details(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderServiceError("Order not found")

        customer = self.customer_dao.get_customer_by_id(order["customer_id"])
        items = self.order_dao.get_order_items(order_id)

        # Add product details to each order item
        detailed_items = []
        for item in items:
            prod = self.product_dao.get_product_by_id(item["product_id"])
            detailed_items.append({
                "order_item_id": item.get("order_item_id"),
                "product": prod,
                "quantity": item["quantity"]
            })

        return {
            "order": order,
            "customer": customer,
            "items": detailed_items
        }

    def list_orders_by_customer(self, customer_id: int) -> List[Dict]:
        cust = self.customer_dao.get_customer_by_id(customer_id)
        if not cust:
            raise OrderServiceError("Customer not found")
        return self.order_dao.list_orders_by_customer(customer_id)

    def cancel_order(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderServiceError("Order not found")
        if order["status"] != "PLACED":
            raise OrderServiceError("Only orders with status PLACED can be cancelled")

        items = self.order_dao.get_order_items(order_id)

        # Restore product stock
        for item in items:
            prod_id = item["product_id"]
            quantity = item["quantity"]
            product = self.product_dao.get_product_by_id(prod_id)
            new_stock = (product.get("stock") or 0) + quantity
            self.product_dao.update_product(prod_id, {"stock": new_stock})

        # Update order status
        updated_order = self.order_dao.update_order_status(order_id, "CANCELLED")
        return updated_order

    def complete_order(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderServiceError("Order not found")
        if order["status"] != "PLACED":
            raise OrderServiceError("Only orders with status PLACED can be marked as Completed")

        updated_order = self.order_dao.update_order_status(order_id, "COMPLETED")
        return updated_order
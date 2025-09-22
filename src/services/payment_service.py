from typing import Optional
from src.dao.payment_dao import PaymentDAO, PaymentDAOError
from src.dao.order_dao import OrderDAO, OrderDAOError

class PaymentServiceError(Exception):
    pass

class PaymentService:
    def __init__(self):
        self.payment_dao = PaymentDAO()
        self.order_dao = OrderDAO()

    def create_pending_payment(self, order_id: int, amount: float) -> dict:
        try:
            return self.payment_dao.create_payment(order_id, amount)
        except PaymentDAOError as e:
            raise PaymentServiceError(str(e))

    def process_payment(self, order_id: int, method: str) -> dict:
        if method not in ("Cash", "Card", "UPI"):
            raise PaymentServiceError("Invalid payment method")

        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise PaymentServiceError("Order not found")
        if order["status"] != "PLACED":
            raise PaymentServiceError("Payment can only be processed for orders with status PLACED")

        payment = self.payment_dao.get_payment_by_order(order_id)
        if not payment:
            raise PaymentServiceError("Payment record not found for order")

        updated_payment = self.payment_dao.update_payment(payment["payment_id"], "PAID", method)
        updated_order = self.order_dao.update_order_status(order_id, "COMPLETED")

        return {
            "payment": updated_payment,
            "order": updated_order
        }

    def refund_payment(self, order_id: int) -> dict:
        payment = self.payment_dao.get_payment_by_order(order_id)
        if not payment:
            raise PaymentServiceError("Payment record not found for order")
        updated_payment = self.payment_dao.update_payment(payment["payment_id"], "REFUNDED")
        return updated_payment
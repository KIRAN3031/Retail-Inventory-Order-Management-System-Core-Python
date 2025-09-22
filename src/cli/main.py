import argparse
import json
from src.services.customer_service import CustomerService, CustomerServiceError
from src.services.product_service import ProductService, ProductServiceError
from src.services.order_service import OrderService, OrderServiceError
from src.services.payment_service import PaymentService, PaymentServiceError
from src.services.reporting_service import ReportingService

class RetailCLI:
    def __init__(self):
        self.customer_service = CustomerService()
        self.product_service = ProductService()
        self.order_service = OrderService()
        self.payment_service = PaymentService()
        self.reporting_service = ReportingService()
        self.parser = self.build_parser()

    # Product commands
    def cmd_product_add(self, args):
        try:
            p = self.product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
            print("Created product:")
            print(json.dumps(p, indent=2, default=str))
        except ProductServiceError as e:
            print("Error:", e)

    def cmd_product_list(self, args):
        ps = self.product_service.list_products(limit=args.limit, category=args.category)
        print(json.dumps(ps, indent=2, default=str))

    # Customer commands
    def cmd_customer_add(self, args):
        try:
            c = self.customer_service.create_customer(args.name, args.email, args.phone, args.city)
            print("Created customer:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerServiceError as e:
            print("Error:", e)

    def cmd_customer_update(self, args):
        try:
            c = self.customer_service.update_customer(args.customer_id, args.phone, args.city)
            print("Updated customer:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerServiceError as e:
            print("Error:", e)

    def cmd_customer_delete(self, args):
        try:
            c = self.customer_service.delete_customer(args.customer_id)
            print("Deleted customer:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerServiceError as e:
            print("Error:", e)

    def cmd_customer_list(self, args):
        cs = self.customer_service.list_customers(limit=args.limit)
        print(json.dumps(cs, indent=2, default=str))

    def cmd_customer_search(self, args):
        cs = self.customer_service.search_customers(email=args.email, city=args.city)
        print(json.dumps(cs, indent=2, default=str))

    # Order commands
    def cmd_order_create(self, args):
        items = []
        for item_str in args.item:
            try:
                pid, qty = item_str.split(":")
                items.append({"prod_id": int(pid), "quantity": int(qty)})
            except Exception:
                print("Invalid item format, expected prod_id:qty:", item_str)
                return
        try:
            ord = self.order_service.create_order(args.customer_id, items)
            print("Order created:")
            print(json.dumps(ord, indent=2, default=str))
        except OrderServiceError as e:
            print("Error:", e)

    def cmd_order_show(self, args):
        try:
            ord_details = self.order_service.get_order_details(args.order_id)
            print(json.dumps(ord_details, indent=2, default=str))
        except OrderServiceError as e:
            print("Error:", e)

    def cmd_order_list(self, args):
        try:
            orders = self.order_service.list_orders_by_customer(args.customer_id)
            print(json.dumps(orders, indent=2, default=str))
        except OrderServiceError as e:
            print("Error:", e)

    def cmd_order_cancel(self, args):
        try:
            ord = self.order_service.cancel_order(args.order_id)
            print("Order cancelled:")
            print(json.dumps(ord, indent=2, default=str))
        except OrderServiceError as e:
            print("Error:", e)

    def cmd_order_complete(self, args):
        try:
            ord = self.order_service.complete_order(args.order_id)
            print("Order marked as Completed:")
            print(json.dumps(ord, indent=2, default=str))
        except OrderServiceError as e:
            print("Error:", e)

    # Payment commands
    def cmd_payment_process(self, args):
        try:
            result = self.payment_service.process_payment(args.order_id, args.method)
            print("Payment processed:")
            print(json.dumps(result, indent=2, default=str))
        except PaymentServiceError as e:
            print("Error:", e)

    def cmd_payment_refund(self, args):
        try:
            refund = self.payment_service.refund_payment(args.order_id)
            print("Payment refunded:")
            print(json.dumps(refund, indent=2, default=str))
        except PaymentServiceError as e:
            print("Error:", e)

    # Reporting commands
    def cmd_report_top_products(self, args):
        data = self.reporting_service.get_top_selling_products(args.top_n)
        print("Top selling products:")
        print(json.dumps(data, indent=2, default=str))

    def cmd_report_revenue(self, args):
        revenue = self.reporting_service.get_total_revenue_last_month()
        print(f"Total revenue last month: {revenue}")

    def cmd_report_order_counts(self, args):
        data = self.reporting_service.get_order_count_per_customer()
        print("Order count per customer:")
        print(json.dumps(data, indent=2, default=str))

    def cmd_report_active_customers(self, args):
        data = self.reporting_service.get_customers_with_multiple_orders(args.min_orders)
        print("Customers with more than 2 orders:")
        print(json.dumps(data, indent=2, default=str))

    def build_parser(self):
        parser = argparse.ArgumentParser(prog="retail-cli")
        sub = parser.add_subparsers(dest="cmd")

        # Product commands
        p_prod = sub.add_parser("product", help="product commands")
        pprod_sub = p_prod.add_subparsers(dest="action")
        addp = pprod_sub.add_parser("add")
        addp.add_argument("--name", required=True)
        addp.add_argument("--sku", required=True)
        addp.add_argument("--price", type=float, required=True)
        addp.add_argument("--stock", type=int, default=0)
        addp.add_argument("--category", default=None)
        addp.set_defaults(func=self.cmd_product_add)

        listp = pprod_sub.add_parser("list")
        listp.add_argument("--limit", type=int, default=100)
        listp.add_argument("--category", default=None)
        listp.set_defaults(func=self.cmd_product_list)

        # Customer commands
        pcust = sub.add_parser("customer", help="customer commands")
        pcust_sub = pcust.add_subparsers(dest="action")

        addc = pcust_sub.add_parser("add")
        addc.add_argument("--name", required=True)
        addc.add_argument("--email", required=True)
        addc.add_argument("--phone", default=None)
        addc.add_argument("--city", default=None)
        addc.set_defaults(func=self.cmd_customer_add)

        updatec = pcust_sub.add_parser("update")
        updatec.add_argument("--customer_id", type=int, required=True)
        updatec.add_argument("--phone", default=None)
        updatec.add_argument("--city", default=None)
        updatec.set_defaults(func=self.cmd_customer_update)

        deletec = pcust_sub.add_parser("delete")
        deletec.add_argument("--customer_id", type=int, required=True)
        deletec.set_defaults(func=self.cmd_customer_delete)

        listc = pcust_sub.add_parser("list")
        listc.add_argument("--limit", type=int, default=100)
        listc.set_defaults(func=self.cmd_customer_list)

        searchc = pcust_sub.add_parser("search")
        searchc.add_argument("--email", default=None)
        searchc.add_argument("--city", default=None)
        searchc.set_defaults(func=self.cmd_customer_search)

        # Order commands
        porder = sub.add_parser("order", help="order commands")
        porder_sub = porder.add_subparsers(dest="action")

        createo = porder_sub.add_parser("create")
        createo.add_argument("--customer_id", type=int, required=True)
        createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
        createo.set_defaults(func=self.cmd_order_create)

        showo = porder_sub.add_parser("show")
        showo.add_argument("--order_id", type=int, required=True)
        showo.set_defaults(func=self.cmd_order_show)

        listo = porder_sub.add_parser("list")
        listo.add_argument("--customer_id", type=int, required=True)
        listo.set_defaults(func=self.cmd_order_list)

        canco = porder_sub.add_parser("cancel")
        canco.add_argument("--order_id", type=int, required=True)
        canco.set_defaults(func=self.cmd_order_cancel)

        compo = porder_sub.add_parser("complete")
        compo.add_argument("--order_id", type=int, required=True)
        compo.set_defaults(func=self.cmd_order_complete)

        # Payment commands
        ppay = sub.add_parser("payment", help="payment commands")
        ppay_sub = ppay.add_subparsers(dest="action")

        process_pay = ppay_sub.add_parser("process")
        process_pay.add_argument("--order_id", type=int, required=True)
        process_pay.add_argument("--method", required=True, choices=["Cash", "Card", "UPI"])
        process_pay.set_defaults(func=self.cmd_payment_process)

        refund_pay = ppay_sub.add_parser("refund")
        refund_pay.add_argument("--order_id", type=int, required=True)
        refund_pay.set_defaults(func=self.cmd_payment_refund)

        # Reporting commands
        prep = sub.add_parser("report", help="reporting commands")
        prep_sub = prep.add_subparsers(dest="action")

        topprod = prep_sub.add_parser("top-products")
        topprod.add_argument("--top_n", type=int, default=5)
        topprod.set_defaults(func=self.cmd_report_top_products)

        revenue = prep_sub.add_parser("revenue")
        revenue.set_defaults(func=self.cmd_report_revenue)

        ordercount = prep_sub.add_parser("order-count")
        ordercount.set_defaults(func=self.cmd_report_order_counts)

        activecust = prep_sub.add_parser("active-customers")
        activecust.add_argument("--min_orders", type=int, default=2)
        activecust.set_defaults(func=self.cmd_report_active_customers)

        return parser

    def run(self):
        args = self.parser.parse_args()
        if not hasattr(args, "func"):
            self.parser.print_help()
            return
        args.func(args)

def main():
    RetailCLI().run()

if __name__ == "__main__":
    main()
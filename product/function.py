from product.models import Product
from order.models import OrderProduct, Order


def suggest_product(id_product):
    orders = Order.objects.all()


suggest_product(1)

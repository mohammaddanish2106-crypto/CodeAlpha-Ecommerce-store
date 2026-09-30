from .cart_utils import get_cart


def cart_item_count(request):
    cart = get_cart(request)
    return {'cart_item_count': cart.total_items}

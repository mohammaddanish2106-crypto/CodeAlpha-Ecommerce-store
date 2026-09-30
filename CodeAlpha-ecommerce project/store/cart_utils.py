from .models import Cart, CartItem


def get_cart(request):
    """Return the current user's cart, creating one if needed.
    Logged-in users get a cart tied to their account.
    Guests get one tied to their session key.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


def merge_session_cart_to_user(request):
    """After login/register, merge any guest session cart items into the
    user's cart so items are not lost on sign-in."""
    if not request.user.is_authenticated:
        return
    if not request.session.session_key:
        return

    try:
        session_cart = Cart.objects.get(
            session_key=request.session.session_key,
            user=None
        )
    except Cart.DoesNotExist:
        return

    if not session_cart.items.exists():
        session_cart.delete()
        return

    user_cart, _ = Cart.objects.get_or_create(user=request.user)

    for session_item in session_cart.items.select_related('product'):
        user_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=session_item.product
        )
        if not created:
            user_item.quantity += session_item.quantity
        else:
            user_item.quantity = session_item.quantity
        user_item.save()

    session_cart.delete()

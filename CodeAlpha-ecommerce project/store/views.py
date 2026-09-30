from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils.text import slugify
from django.http import HttpResponseForbidden
from functools import wraps

from .models import Category, Product, CartItem, Order, OrderItem, UserProfile, Cart
from .forms import RegisterForm, CheckoutForm, ProductForm, OrderStatusForm, ProfileUpdateForm
from .cart_utils import get_cart, merge_session_cart_to_user


# ─────────────────────────────────────────────────────────────────────────────
# Role-based access decorators
# ─────────────────────────────────────────────────────────────────────────────

def staff_required(view_func):
    """Allows staff and admin roles only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access that page.")
            return redirect('login')
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_staff_or_admin:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden(
            "<h2>403 – Access Denied</h2><p>You do not have permission to view this page.</p>"
        )
    return wrapper


def admin_required(view_func):
    """Allows admin role only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access that page.")
            return redirect('login')
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_admin_role:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden(
            "<h2>403 – Access Denied</h2><p>Admin access required.</p>"
        )
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# Landing Page
# ─────────────────────────────────────────────────────────────────────────────

def landing(request):
    categories = Category.objects.all()
    featured_products = (
        Product.objects
        .filter(stock__gt=0)
        .select_related('category')
        .order_by('-created_at')[:8]
    )
    return render(request, 'store/landing.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Products
# ─────────────────────────────────────────────────────────────────────────────

def product_list(request):
    products = Product.objects.all().select_related('category')
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'active_category': category_slug,
        'query': query or '',
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related': related,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Cart  (login required for all cart actions)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def cart_detail(request):
    cart = get_cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not product.in_stock:
        messages.error(request, f"<strong>{product.name}</strong> is currently out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'product_list'))

    cart = get_cart(request)
    quantity = max(1, int(request.POST.get('quantity', 1)))

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity = item.quantity + quantity if not created else quantity
    item.save()

    messages.success(request, f"<strong>{product.name}</strong> added to your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'cart_detail'))


@login_required
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=get_cart(request))
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
        messages.info(request, "Item removed from cart.")
    return redirect('cart_detail')


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=get_cart(request))
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart_detail')


# ─────────────────────────────────────────────────────────────────────────────
# Checkout / Orders
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart = get_cart(request)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.total_price = cart.total_price
                order.save()

                for item in cart.items.select_related('product'):
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.price,
                        quantity=item.quantity,
                    )
                    item.product.stock = max(0, item.product.stock - item.quantity)
                    item.product.save()

                cart.items.all().delete()

            messages.success(
                request,
                "🎉 Order placed successfully! Thank you for shopping with us."
            )
            return redirect('order_detail', order_id=order.id)
    else:
        initial = {}
        profile = getattr(request.user, 'profile', None)
        if request.user.first_name:
            initial['full_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        if profile:
            initial.setdefault('address', profile.address)
            initial.setdefault('city', profile.city)
            initial.setdefault('phone', profile.phone)
        form = CheckoutForm(initial=initial)

    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def order_cancel(request, order_id):
    """Customer can cancel their own pending orders."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ('pending', 'processing'):
        messages.error(request, "This order can no longer be cancelled.")
        return redirect('order_detail', order_id=order.id)

    if request.method == 'POST':
        with transaction.atomic():
            # Restore stock
            for item in order.items.select_related('product'):
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
            order.status = 'cancelled'
            order.save()
        messages.success(request, f"Order #{order.id} has been cancelled.")
        return redirect('order_list')

    return render(request, 'store/order_cancel_confirm.html', {'order': order})


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('landing')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure profile exists and set defaults
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = 'customer'
            profile.save()
            login(request, user)
            # Merge any guest cart items into the new user's cart
            merge_session_cart_to_user(request)
            messages.success(request, f"Welcome to ShopEasy, {user.first_name or user.username}! 🎉")
            return redirect('landing')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# User Profile
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile_obj)
        if form.is_valid():
            # Update User fields
            user = request.user
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name  = form.cleaned_data.get('last_name',  user.last_name)
            user.email      = form.cleaned_data.get('email',       user.email)
            user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(
            instance=profile_obj,
            initial={
                'first_name': request.user.first_name,
                'last_name':  request.user.last_name,
                'email':      request.user.email,
            }
        )
    recent_orders = Order.objects.filter(user=request.user)[:5]
    return render(request, 'store/profile.html', {
        'form': form,
        'profile': profile_obj,
        'recent_orders': recent_orders,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Staff Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@staff_required
def staff_dashboard(request):
    # Summary stats
    total_orders    = Order.objects.count()
    pending_orders  = Order.objects.filter(status='pending').count()
    total_products  = Product.objects.count()
    low_stock       = Product.objects.filter(stock__lte=5, stock__gt=0).count()
    out_of_stock    = Product.objects.filter(stock=0).count()
    total_customers = User.objects.filter(profile__role='customer').count()
    revenue         = Order.objects.exclude(status='cancelled').aggregate(
        total=Sum('total_price')
    )['total'] or 0

    recent_orders   = Order.objects.select_related('user').order_by('-created_at')[:10]
    low_stock_items = Product.objects.filter(stock__lte=5).order_by('stock')[:10]

    return render(request, 'store/staff_dashboard.html', {
        'total_orders':    total_orders,
        'pending_orders':  pending_orders,
        'total_products':  total_products,
        'low_stock':       low_stock,
        'out_of_stock':    out_of_stock,
        'total_customers': total_customers,
        'revenue':         revenue,
        'recent_orders':   recent_orders,
        'low_stock_items': low_stock_items,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Staff – Order Management
# ─────────────────────────────────────────────────────────────────────────────

@staff_required
def staff_orders(request):
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    query = request.GET.get('q', '')
    if query:
        orders = orders.filter(
            Q(user__username__icontains=query) |
            Q(full_name__icontains=query) |
            Q(id__icontains=query)
        )
    return render(request, 'store/staff_orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'query': query,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_required
def staff_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.id} status updated to '{order.get_status_display()}'.")
            return redirect('staff_order_detail', order_id=order.id)
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'store/staff_order_detail.html', {'order': order, 'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# Staff – Product Management
# ─────────────────────────────────────────────────────────────────────────────

@staff_required
def staff_products(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'store/staff_products.html', {
        'products': products,
        'query': query,
    })


@staff_required
def staff_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.slug = slugify(product.name)
            # Ensure slug uniqueness
            base_slug = product.slug
            counter = 1
            while Product.objects.filter(slug=product.slug).exists():
                product.slug = f"{base_slug}-{counter}"
                counter += 1
            product.save()
            messages.success(request, f"Product '{product.name}' added successfully.")
            return redirect('staff_products')
    else:
        form = ProductForm()
    return render(request, 'store/staff_product_form.html', {
        'form': form,
        'action': 'Add',
    })


@staff_required
def staff_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('staff_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/staff_product_form.html', {
        'form': form,
        'product': product,
        'action': 'Edit',
    })


@staff_required
def staff_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' deleted.")
        return redirect('staff_products')
    return render(request, 'store/staff_product_delete.html', {'product': product})


# ─────────────────────────────────────────────────────────────────────────────
# Admin – User Management (admin role only)
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def admin_users(request):
    users = User.objects.select_related('profile').order_by('-date_joined')
    query = request.GET.get('q', '')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query)
        )
    return render(request, 'store/admin_users.html', {
        'users': users,
        'query': query,
    })


@admin_required
def admin_user_role(request, user_id):
    """Change a user's role (admin only)."""
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot change your own role.")
        return redirect('admin_users')

    profile, _ = UserProfile.objects.get_or_create(user=target_user)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(UserProfile.ROLE_CHOICES):
            profile.role = new_role
            profile.save()
            messages.success(
                request,
                f"{target_user.username}'s role changed to '{new_role}'."
            )
        return redirect('admin_users')

    return render(request, 'store/admin_user_role.html', {
        'target_user': target_user,
        'profile': profile,
        'role_choices': UserProfile.ROLE_CHOICES,
    })

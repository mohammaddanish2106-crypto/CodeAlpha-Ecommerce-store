from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


class CartAwareLoginView(auth_views.LoginView):
    """Standard login view that also merges the guest cart on sign-in."""
    template_name = 'store/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        from .cart_utils import merge_session_cart_to_user
        merge_session_cart_to_user(self.request)
        return response


urlpatterns = [
    # ── Public ──────────────────────────────────────────────────────────────
    path('', views.landing, name='landing'),
    path('shop/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # ── Cart (login required) ────────────────────────────────────────────────
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),

    # ── Checkout / Orders ────────────────────────────────────────────────────
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),

    # ── Auth ─────────────────────────────────────────────────────────────────
    path('register/', views.register, name='register'),
    path('login/', CartAwareLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),

    # ── User Profile ─────────────────────────────────────────────────────────
    path('profile/', views.profile, name='profile'),

    # ── Staff Panel ──────────────────────────────────────────────────────────
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/orders/', views.staff_orders, name='staff_orders'),
    path('staff/orders/<int:order_id>/', views.staff_order_detail, name='staff_order_detail'),
    path('staff/products/', views.staff_products, name='staff_products'),
    path('staff/products/add/', views.staff_product_add, name='staff_product_add'),
    path('staff/products/<int:product_id>/edit/', views.staff_product_edit, name='staff_product_edit'),
    path('staff/products/<int:product_id>/delete/', views.staff_product_delete, name='staff_product_delete'),

    # ── Admin Panel (role=admin only) ─────────────────────────────────────────
    path('manage/users/', views.admin_users, name='admin_users'),
    path('manage/users/<int:user_id>/role/', views.admin_user_role, name='admin_user_role'),
]

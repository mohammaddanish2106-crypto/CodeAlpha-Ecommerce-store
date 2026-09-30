from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Sum
from .models import Category, Product, Cart, CartItem, Order, OrderItem, UserProfile


# ─────────────────────────────────────────────────────────────────────────────
# Admin Site Customisation
# ─────────────────────────────────────────────────────────────────────────────
admin.site.site_header  = "ShopEasy Administration"
admin.site.site_title   = "ShopEasy Admin"
admin.site.index_title  = "Store Management"


# ─────────────────────────────────────────────────────────────────────────────
# UserProfile inline – shown on the User page
# ─────────────────────────────────────────────────────────────────────────────
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile & Role'
    fields = ('role', 'phone', 'address', 'city')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display  = ('username', 'email', 'first_name', 'last_name', 'get_role',
                     'is_active', 'date_joined')
    list_filter   = ('is_active', 'is_staff', 'profile__role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)

    @admin.display(description='Role')
    def get_role(self, obj):
        profile = getattr(obj, 'profile', None)
        role = profile.role if profile else '—'
        colours = {'admin': '#e74c3c', 'staff': '#e67e22', 'customer': '#27ae60'}
        colour = colours.get(role, '#95a5a6')
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            colour, role.capitalize()
        )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ─────────────────────────────────────────────────────────────────────────────
# UserProfile (standalone)
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'role', 'phone', 'city', 'created_at')
    list_filter   = ('role',)
    search_fields = ('user__username', 'user__email', 'city')
    list_editable = ('role',)
    ordering      = ('-created_at',)


# ─────────────────────────────────────────────────────────────────────────────
# Category
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display       = ('name', 'slug', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields      = ('name',)

    @admin.display(description='# Products')
    def product_count(self, obj):
        return obj.products.count()


# ─────────────────────────────────────────────────────────────────────────────
# Product
# ─────────────────────────────────────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display        = ('name', 'category', 'price', 'stock', 'stock_status',
                           'image_preview', 'created_at')
    list_filter         = ('category', 'created_at')
    search_fields       = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable       = ('price', 'stock')
    readonly_fields     = ('created_at', 'image_preview')
    ordering            = ('-created_at',)
    actions             = ['mark_out_of_stock', 'mark_in_stock']

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Stock Status')
    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color:#e74c3c;font-weight:600;">Out of Stock</span>')
        if obj.stock <= 5:
            return format_html('<span style="color:#e67e22;font-weight:600;">Low ({})</span>', obj.stock)
        return format_html('<span style="color:#27ae60;font-weight:600;">In Stock</span>')

    @admin.display(description='Image')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px;" />',
                obj.image.url
            )
        return '—'

    @admin.action(description='Mark selected products as out of stock')
    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(stock=0)
        self.message_user(request, f"{updated} product(s) marked as out of stock.")

    @admin.action(description='Set stock to 10 for selected products')
    def mark_in_stock(self, request, queryset):
        updated = queryset.update(stock=10)
        self.message_user(request, f"{updated} product(s) restocked to 10.")


# ─────────────────────────────────────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model        = OrderItem
    extra        = 0
    readonly_fields = ('product', 'price', 'quantity', 'subtotal')
    can_delete   = False

    @admin.display(description='Subtotal')
    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ('id', 'user', 'full_name', 'city', 'status_badge',
                       'total_price', 'created_at')
    list_filter     = ('status', 'created_at', 'city')
    search_fields   = ('user__username', 'full_name', 'phone', 'city')
    list_editable   = ('status',)  # quick status change from list view — note: removed status_badge from editable
    readonly_fields = ('user', 'total_price', 'created_at')
    ordering        = ('-created_at',)
    inlines         = [OrderItemInline]
    actions         = ['mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    # Override list_display to separate read-only badge from editable status
    list_display    = ('id', 'user', 'full_name', 'city', 'status',
                       'total_price', 'created_at')

    fieldsets = (
        ('Customer', {
            'fields': ('user', 'full_name', 'address', 'city', 'phone')
        }),
        ('Order Info', {
            'fields': ('status', 'total_price', 'created_at')
        }),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        colours = {
            'pending':    '#f39c12',
            'processing': '#3498db',
            'shipped':    '#9b59b6',
            'delivered':  '#27ae60',
            'cancelled':  '#e74c3c',
        }
        colour = colours.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            colour, obj.get_status_display()
        )

    @admin.action(description='Mark selected orders as Processing')
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, "Orders marked as Processing.")

    @admin.action(description='Mark selected orders as Shipped')
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, "Orders marked as Shipped.")

    @admin.action(description='Mark selected orders as Delivered')
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, "Orders marked as Delivered.")

    @admin.action(description='Mark selected orders as Cancelled')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, "Orders marked as Cancelled.")


# ─────────────────────────────────────────────────────────────────────────────
# Cart & CartItem
# ─────────────────────────────────────────────────────────────────────────────
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'session_key', 'total_items', 'total_price', 'created_at')
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('user', 'session_key', 'created_at')
    inlines       = [CartItemInline]

    @admin.display(description='Items')
    def total_items(self, obj):
        return obj.total_items

    @admin.display(description='Total')
    def total_price(self, obj):
        return f"${obj.total_price:.2f}"

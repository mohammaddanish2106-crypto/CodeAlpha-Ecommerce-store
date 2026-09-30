# ShopEasy — Django E-commerce Platform

A full-featured e-commerce web application built with **Django 4.2** and **MySQL**.  
Includes role-based access control, a staff management panel, a rich Django admin, and a complete shopping flow.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Quick Start](#quick-start)
5. [Database Setup](#database-setup)
6. [User Roles](#user-roles)
7. [URL Reference](#url-reference)
8. [Django Admin](#django-admin)
9. [Seed Data](#seed-data)
10. [Environment Notes](#environment-notes)

---

## Features

### Shopping
- Product catalogue with category filter, keyword search, and price/newest sorting
- Product detail pages with related product suggestions
- Persistent cart — guest carts (session-based) are merged into the user's cart on login
- Stock validation — out-of-stock products cannot be added to the cart
- Checkout with delivery details pre-filled from the user profile

### Orders
- Full order lifecycle: Pending → Processing → Shipped → Delivered
- Customers can cancel their own Pending or Processing orders (stock is automatically restored)
- Per-order detail page with item breakdown and shipping info

### Authentication & Security
- Registration collects first name, last name, email, username, and password
- All cart and checkout actions require login — guests are redirected to the login page
- CSRF protection on all forms; ownership checks on orders (users can only view their own)
- Passwords validated against Django's built-in strength rules

### Role-Based Access Control
| Role | Access |
|---|---|
| **Customer** | Shop, cart, checkout, orders, profile |
| **Staff** | Everything above + staff dashboard, manage all orders & products |
| **Admin** | Everything above + user management, role assignment, Django admin |

### Staff Panel (`/staff/`)
- Dashboard: revenue, order counts, low-stock alerts, recent orders
- Order management: filter by status, search, update status per order
- Product management: add, edit, delete products with image upload

### Admin Panel (`/manage/`)
- User list with search, role badges, active status
- Change any user's role (cannot change your own)

### Django Admin (`/admin/`)
- Customised site header and titles
- Product admin with image preview, inline price/stock editing, bulk restock/out-of-stock actions
- Order admin with coloured status badges and bulk status actions
- User admin with role inline and coloured role labels
- Cart admin with item inline

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x, Django 4.2 |
| Database | MySQL 8+ via `mysqlclient` |
| Frontend | HTML5, CSS3 (custom design system), Vanilla JS |
| Icons | Font Awesome 6.5 |
| Fonts | Google Fonts — Inter |
| Images | Pillow (Django `ImageField`) |

---

## Project Structure

```
ecommerce_project/
│
├── manage.py
│
├── ecommerce/                   # Project package
│   ├── settings.py              # Main settings (imports DB config)
│   ├── db_config.py             # ← Database credentials (edit this)
│   ├── urls.py                  # Root URL dispatcher
│   ├── wsgi.py
│   └── asgi.py
│
├── store/                       # Main application
│   ├── models.py                # UserProfile, Category, Product, Cart, CartItem, Order, OrderItem
│   ├── views.py                 # All views + role decorators
│   ├── urls.py                  # URL patterns
│   ├── forms.py                 # RegisterForm, ProfileUpdateForm, CheckoutForm, ProductForm, OrderStatusForm
│   ├── admin.py                 # Rich admin registrations
│   ├── cart_utils.py            # get_cart(), merge_session_cart_to_user()
│   ├── context_processors.py   # cart_item_count injected into every template
│   ├── apps.py
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py     # Management command to load sample data
│   └── templates/store/
│       ├── landing.html         # Home page
│       ├── product_list.html    # Shop / catalogue
│       ├── product_detail.html  # Single product
│       ├── cart_detail.html     # Cart
│       ├── checkout.html        # Checkout
│       ├── order_list.html      # Customer order history
│       ├── order_detail.html    # Single order + cancel button
│       ├── order_cancel_confirm.html
│       ├── profile.html         # User profile editor
│       ├── register.html        # Sign-up
│       ├── login.html           # Sign-in
│       ├── staff_dashboard.html # Staff overview
│       ├── staff_orders.html    # Staff order list
│       ├── staff_order_detail.html
│       ├── staff_products.html  # Staff product list
│       ├── staff_product_form.html  # Add / edit product
│       ├── staff_product_delete.html
│       ├── admin_users.html     # Admin user list
│       └── admin_user_role.html # Admin role change
│
├── templates/
│   └── base.html                # Site-wide layout, navbar, footer
│
├── static/
│   ├── css/style.css            # Complete design system
│   └── js/script.js
│
└── media/
    └── products/                # Uploaded / seeded product images
```

---

## Quick Start

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd ecommerce_project

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Windows note:** If `mysqlclient` fails to install, download the matching `.whl`
> from [Christoph Gohlke's wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient)
> and install it with `pip install <filename>.whl`.

### 3. Configure the database

Open **`ecommerce/db_config.py`** and set your MySQL credentials:

```python
DB_NAME     = 'ecommerce_db'
DB_USER     = 'root'       # your MySQL username
DB_PASSWORD = ''           # your MySQL password
DB_HOST     = 'localhost'
DB_PORT     = '3306'
```

That is the **only file** you need to edit for database configuration.

### 4. Create the MySQL database

```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (gets admin role automatically)

```bash
python manage.py createsuperuser
```

After creation, run this once to assign the admin role to that superuser:

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from store.models import UserProfile
for u in User.objects.filter(is_superuser=True):
    p, _ = UserProfile.objects.get_or_create(user=u)
    p.role = 'admin'; p.save()
    print(f'Admin role set for: {u.username}')
"
```

### 7. Load sample data (optional)

```bash
python manage.py seed_data
```

This seeds 6 categories, 24 products, and downloads product images from Unsplash.

### 8. Start the development server

```bash
python manage.py runserver
```

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Home page |
| `http://127.0.0.1:8000/shop/` | Product catalogue |
| `http://127.0.0.1:8000/admin/` | Django admin |
| `http://127.0.0.1:8000/staff/` | Staff dashboard |
| `http://127.0.0.1:8000/manage/users/` | Admin user management |

---

## Database Setup

All database connection settings are in **`ecommerce/db_config.py`**.  
`settings.py` imports from that file — you never need to touch `settings.py` for DB changes.

```
ecommerce/db_config.py   ← edit credentials here
ecommerce/settings.py    ← imports DATABASES from db_config (do not edit)
```

### Schema overview

| Table | Model | Description |
|---|---|---|
| `store_userprofile` | `UserProfile` | Role (customer/staff/admin), phone, address |
| `store_category` | `Category` | Product categories with slugs |
| `store_product` | `Product` | Catalogue items with image, stock, price |
| `store_cart` | `Cart` | One per user (or session for guests) |
| `store_cartitem` | `CartItem` | Products + quantities inside a cart |
| `store_order` | `Order` | Placed orders with delivery details |
| `store_orderitem` | `OrderItem` | Line items inside an order (price snapshot) |

---

## User Roles

Roles are stored in `UserProfile.role` and enforced by decorators in `views.py`.

| Role | Assigned by | Access |
|---|---|---|
| `customer` | Auto on registration | Shop, cart, orders, profile |
| `staff` | Admin via `/manage/users/` or Django admin | + Staff panel, product & order management |
| `admin` | Superuser flag or via another admin | + User management, role assignment, Django admin |

Superusers created with `createsuperuser` should have their role set to `admin` (see Quick Start step 6).

---

## URL Reference

### Public
| URL | View | Description |
|---|---|---|
| `/` | `landing` | Home page |
| `/shop/` | `product_list` | Catalogue (filter, search, sort) |
| `/product/<slug>/` | `product_detail` | Product detail |
| `/register/` | `register` | Sign up |
| `/login/` | `CartAwareLoginView` | Sign in (merges guest cart) |
| `/logout/` | `LogoutView` | Sign out |

### Customer (login required)
| URL | View | Description |
|---|---|---|
| `/cart/` | `cart_detail` | View cart |
| `/cart/add/<id>/` | `cart_add` | Add to cart |
| `/cart/update/<id>/` | `cart_update` | Change quantity |
| `/cart/remove/<id>/` | `cart_remove` | Remove item |
| `/checkout/` | `checkout` | Place order |
| `/orders/` | `order_list` | Order history |
| `/orders/<id>/` | `order_detail` | Order detail |
| `/orders/<id>/cancel/` | `order_cancel` | Cancel pending order |
| `/profile/` | `profile` | Edit profile |

### Staff (role: staff or admin)
| URL | Description |
|---|---|
| `/staff/` | Dashboard with stats |
| `/staff/orders/` | All orders, filter/search |
| `/staff/orders/<id>/` | Update order status |
| `/staff/products/` | Product catalogue management |
| `/staff/products/add/` | Add new product |
| `/staff/products/<id>/edit/` | Edit product |
| `/staff/products/<id>/delete/` | Delete product |

### Admin (role: admin only)
| URL | Description |
|---|---|
| `/manage/users/` | User list with roles |
| `/manage/users/<id>/role/` | Change user role |
| `/admin/` | Django admin panel |

---

## Django Admin

Accessible at `/admin/` for superusers.

- **Products** — inline image preview, editable price/stock in list view, bulk actions to restock or mark out-of-stock
- **Orders** — coloured status badges, bulk status updates (Processing / Shipped / Delivered / Cancelled), order items inline
- **Users** — role displayed with colour coding, inline profile editor
- **Categories** — auto slug generation
- **Carts** — item inline, total price/items displayed

---

## Seed Data

```bash
python manage.py seed_data
```

Creates:
- 6 categories: Electronics, Clothing, Books, Home & Kitchen, Sports, Beauty
- 24 products with descriptions, prices, stock levels, and downloaded images
- Images are saved to `media/products/` and linked to product records

Re-running the command is safe — it uses `get_or_create` and updates existing records.

---

## Environment Notes

- `DEBUG = True` in `settings.py` — set to `False` for any public deployment
- `SECRET_KEY` in `settings.py` is a placeholder — replace it with a strong random key in production
- `ALLOWED_HOSTS = ['*']` — restrict to your domain in production
- Media files are served by Django in development (`DEBUG=True`) — use a web server (nginx, S3) in production
- No `.env` file is used by default; for production consider [python-decouple](https://pypi.org/project/python-decouple/) or [django-environ](https://pypi.org/project/django-environ/) to keep secrets out of source code

"""
Database configuration for ShopEasy.

Edit the values below to match your local (or production) MySQL setup,
then import this module in settings.py — settings.py is already wired up
to read DATABASES from here, so you never need to touch settings.py for
database changes.

Steps to get started
---------------------
1. Make sure MySQL is running and create the database once:
       CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

2. Fill in DB_USER and DB_PASSWORD below.

3. Leave the rest as-is for a standard local setup.
"""

# ─── Connection details ────────────────────────────────────────────────────
DB_NAME     = 'ecommerce_db'
DB_USER     = 'root'          # ← change to your MySQL username
DB_PASSWORD = ''              # ← change to your MySQL password
DB_HOST     = 'localhost'
DB_PORT     = '3306'

# ─── Django DATABASES dict ─────────────────────────────────────────────────
# This is imported directly by settings.py.
DATABASES = {
    'default': {
        'ENGINE':  'django.db.backends.mysql',
        'NAME':    DB_NAME,
        'USER':    DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST':    DB_HOST,
        'PORT':    DB_PORT,
        'OPTIONS': {
            # Enforce strict SQL mode to catch data errors early.
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            # Use utf8mb4 for full Unicode (emoji, etc.)
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 60,   # keep connections alive for 60 s (production tuning)
    }
}

import urllib.request
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from store.models import Category, Product


class Command(BaseCommand):
    help = "Seed the database with sample categories and products (with images)"

    PRODUCTS = [
        # (name, category, price, stock, description, image_url)
        # --- Electronics ---
        ('Wireless Noise-Cancelling Headphones', 'Electronics', 79.99, 25,
         'Premium over-ear headphones with active noise cancellation, 30-hour battery life and crystal-clear sound.',
         'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80'),
        ('Smart Watch Pro', 'Electronics', 129.99, 15,
         'Feature-packed smartwatch with health tracking, GPS, heart-rate monitor and 7-day battery.',
         'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&q=80'),
        ('Bluetooth Speaker', 'Electronics', 49.99, 30,
         'Portable waterproof Bluetooth speaker with 360° surround sound and 12-hour playtime.',
         'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&q=80'),
        ('Laptop Stand', 'Electronics', 34.99, 40,
         'Ergonomic aluminium laptop stand, adjustable height, compatible with all laptops 10–17 inches.',
         'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80'),
        ('Mechanical Keyboard', 'Electronics', 89.99, 20,
         'Compact TKL mechanical keyboard with RGB backlighting and tactile blue switches.',
         'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80'),
        ('USB-C Hub 7-in-1', 'Electronics', 44.99, 35,
         'Multi-port USB-C hub: HDMI 4K, 3×USB-A, SD card reader, PD charging and Ethernet.',
         'https://images.unsplash.com/photo-1625895197185-efcec01cffe0?w=600&q=80'),

        # --- Clothing ---
        ('Classic White T-Shirt', 'Clothing', 19.99, 60,
         '100% organic cotton crew-neck T-shirt. Breathable, pre-shrunk and available in all sizes.',
         'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80'),
        ('Premium Denim Jacket', 'Clothing', 59.99, 20,
         'Vintage-wash denim jacket with button front, chest pockets and relaxed modern fit.',
         'https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=600&q=80'),
        ('Running Sneakers', 'Clothing', 74.99, 45,
         'Lightweight performance running shoes with foam cushioning and breathable mesh upper.',
         'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80'),
        ('Cozy Hoodie', 'Clothing', 44.99, 35,
         'Soft fleece pullover hoodie with kangaroo pocket and adjustable drawstring hood.',
         'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&q=80'),
        ('Slim Fit Chinos', 'Clothing', 39.99, 28,
         'Smart-casual slim-fit chino trousers in stretch cotton. Perfect for work or weekend.',
         'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80'),

        # --- Books ---
        ('Python Crash Course', 'Books', 27.99, 50,
         'The best-selling beginner Python book. Covers data structures, functions, OOP and real projects.',
         'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600&q=80'),
        ('The Pragmatic Programmer', 'Books', 34.99, 30,
         'Classic software engineering guide covering career tips, coding practices and architecture.',
         'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80'),
        ('Atomic Habits', 'Books', 16.99, 55,
         'James Clear\'s #1 bestseller on building good habits and breaking bad ones through tiny changes.',
         'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&q=80'),
        ('Dune (Sci-Fi Classic)', 'Books', 14.99, 40,
         'Frank Herbert\'s epic science-fiction masterpiece set in a distant future interstellar society.',
         'https://images.unsplash.com/photo-1600189261867-30e5ffe7b8da?w=600&q=80'),

        # --- Home & Kitchen ---
        ('Non-Stick Frying Pan', 'Home & Kitchen', 29.99, 25,
         '28cm non-stick frying pan with ergonomic heat-resistant handle. Induction compatible.',
         'https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&q=80'),
        ('Espresso Coffee Maker', 'Home & Kitchen', 89.99, 12,
         '15-bar pressure espresso machine with milk frother. Brews espresso, cappuccino and latte.',
         'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=600&q=80'),
        ('Ceramic Dinner Set', 'Home & Kitchen', 54.99, 18,
         '16-piece ceramic dinnerware set: plates, bowls and mugs. Dishwasher and microwave safe.',
         'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=600&q=80'),
        ('Scented Candle Set', 'Home & Kitchen', 22.99, 40,
         'Set of 3 hand-poured soy wax candles in calming lavender, vanilla and sandalwood scents.',
         'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600&q=80'),

        # --- Sports ---
        ('Yoga Mat Premium', 'Sports', 39.99, 30,
         'Non-slip 6mm thick TPE yoga mat with alignment lines, carry strap and sweat-resistant surface.',
         'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&q=80'),
        ('Adjustable Dumbbells', 'Sports', 119.99, 10,
         'Space-saving adjustable dumbbell set from 2.5kg to 25kg. Perfect for home workouts.',
         'https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=600&q=80'),
        ('Water Bottle 1L', 'Sports', 18.99, 50,
         'Insulated stainless steel water bottle that keeps drinks cold 24h or hot 12h. Leak-proof.',
         'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&q=80'),

        # --- Beauty ---
        ('Skincare Essentials Kit', 'Beauty', 49.99, 20,
         'Daily skincare set: gentle cleanser, hydrating toner, vitamin C serum and SPF moisturiser.',
         'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&q=80'),
        ('Perfume Collection Set', 'Beauty', 69.99, 15,
         'Luxury gift set of 4 eau de parfum miniatures in floral, woody, citrus and oriental notes.',
         'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=600&q=80'),
    ]

    def handle(self, *args, **options):
        categories = ['Electronics', 'Clothing', 'Books', 'Home & Kitchen', 'Sports', 'Beauty']
        cat_objs = {}
        for name in categories:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            cat_objs[name] = cat
        self.stdout.write(self.style.SUCCESS(f"✓ {len(categories)} categories ready"))

        media_products = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_products, exist_ok=True)

        created = 0
        updated = 0
        for (name, cat_name, price, stock, desc, img_url) in self.PRODUCTS:
            slug = slugify(name)
            product, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'category': cat_objs[cat_name],
                    'price': price,
                    'stock': stock,
                    'description': desc,
                }
            )
            if not was_created:
                product.category = cat_objs[cat_name]
                product.price = price
                product.stock = stock
                product.description = desc
                updated += 1

            # Download image if not already saved
            img_filename = f"{slug}.jpg"
            img_path = os.path.join(media_products, img_filename)
            if not os.path.exists(img_path):
                try:
                    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        with open(img_path, 'wb') as f:
                            f.write(resp.read())
                    product.image = f'products/{img_filename}'
                    self.stdout.write(f"  ↓ Downloaded image for {name}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ✗ Image failed for {name}: {e}"))
            else:
                product.image = f'products/{img_filename}'

            product.save()
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"✓ {created} products created, {updated} updated — {len(self.PRODUCTS)} total"
        ))

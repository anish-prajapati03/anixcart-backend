import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from store.models import Product

Product.objects.all().delete()

products = [
    {"name": "Wireless Headphones", "description": "Premium noise-cancelling headphones with 30hr battery", "price": 8299.00, "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", "stock": 15, "category": "audio"},
    {"name": "Bluetooth Speaker", "description": "Portable waterproof speaker with deep bass", "price": 2999.00, "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400", "stock": 18, "category": "audio"},
    {"name": "Mechanical Keyboard", "description": "RGB backlit mechanical gaming keyboard", "price": 6599.00, "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400", "stock": 8, "category": "peripherals"},
    {"name": "Mouse Pad XL", "description": "Extra large gaming mouse pad with stitched edges", "price": 899.00, "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400", "stock": 50, "category": "peripherals"},
    {"name": "USB-C Hub", "description": "7-in-1 multiport USB-C hub for laptops", "price": 3299.00, "image": "https://images.unsplash.com/photo-1625895197185-efcec01cffe0?w=400", "stock": 25, "category": "accessories"},
    {"name": "Laptop Stand", "description": "Adjustable aluminium laptop stand", "price": 1799.00, "image": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400", "stock": 30, "category": "accessories"},
    {"name": "Webcam HD", "description": "1080p HD webcam with built-in microphone", "price": 4999.00, "image": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=400", "stock": 12, "category": "electronics"},
    {"name": "Smart Watch", "description": "Fitness tracker with heart rate monitor", "price": 12499.00, "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400", "stock": 20, "category": "wearables"},
]

for p in products:
    Product.objects.create(**p)

print(f"Created {len(products)} products with categories!")

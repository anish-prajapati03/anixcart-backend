from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CartItemSerializer, OrderSerializer
import re


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Product.objects.all().order_by('-created_at')
        category = self.request.query_params.get('category')
        if category and category != 'all':
            qs = qs.filter(category=category)
        return qs


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=400)
    user = User.objects.create_user(username=username, password=password, email=email)
    refresh = RefreshToken.for_user(user)
    return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'username': user.username})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_list(request):
    items = CartItem.objects.filter(user=request.user).select_related('product')
    return Response(CartItemSerializer(items, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_add(request):
    product_id = request.data.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.qty += 1
        item.save()
    return Response(CartItemSerializer(item).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_remove(request, item_id):
    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return Response(status=204)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_clear(request):
    CartItem.objects.filter(user=request.user).delete()
    return Response(status=204)


@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot(request):
    msg = request.data.get('message', '').lower().strip()
    user = request.user if request.user.is_authenticated else None

    # ── Greetings ──
    if re.search(r'\b(hi|hello|hey|namaste|hii|helo)\b', msg):
        name = f', {user.username}' if user else ''
        return Response({'reply': f"👋 Hey{name}! Welcome to AnixCart. How can I help you today?\n\nYou can ask me about:\n• 🛍️ Products & categories\n• 💰 Prices\n• 🛒 Your cart\n• 📦 Your orders\n• 🚚 Delivery info\n• 💳 Payment methods"})

    # ── Products / categories ──
    if re.search(r'product|item|sell|available|show|what do you have', msg):
        products = Product.objects.all()
        categories = list(set(products.values_list('category', flat=True)))
        cat_list = ', '.join(c.capitalize() for c in categories)
        return Response({'reply': f"🛍️ We have {products.count()} products across these categories:\n\n📂 {cat_list}\n\nUse the category dropdown on the homepage to filter products!"})

    # ── Category specific ──
    for cat in ['electronics', 'audio', 'accessories', 'wearables', 'peripherals']:
        if cat in msg:
            items = Product.objects.filter(category=cat)
            if items.exists():
                names = '\n'.join(f"• {p.name} — ₹{p.price:,.0f}" for p in items[:5])
                return Response({'reply': f"🗂️ Here are our {cat.capitalize()} products:\n\n{names}\n\nClick the category dropdown to browse them!"})
            return Response({'reply': f"😕 No products found in {cat.capitalize()} right now. Check back soon!"})

    # ── Price / cheap / expensive ──
    if re.search(r'cheap|lowest|budget|affordable|minimum price|low price', msg):
        p = Product.objects.order_by('price').first()
        return Response({'reply': f"💸 Our most affordable product is:\n\n🏷️ {p.name}\n💰 ₹{p.price:,.0f}\n\nGreat value for money!"})

    if re.search(r'expensive|highest|premium|best|top|maximum price|high price', msg):
        p = Product.objects.order_by('-price').first()
        return Response({'reply': f"👑 Our premium product is:\n\n🏷️ {p.name}\n💰 ₹{p.price:,.0f}\n\nTop quality guaranteed!"})

    if re.search(r'price|cost|how much|rate', msg):
        products = Product.objects.all().order_by('price')
        lines = '\n'.join(f"• {p.name} — ₹{p.price:,.0f}" for p in products[:6])
        return Response({'reply': f"💰 Here are our product prices:\n\n{lines}\n\nAll prices include taxes!"})

    # ── Cart ──
    if re.search(r'cart|basket|bag', msg):
        if not user:
            return Response({'reply': "🔒 Please login first to view your cart.\n\nClick **Login / Sign Up** in the top right corner!"})
        items = CartItem.objects.filter(user=user).select_related('product')
        if not items.exists():
            return Response({'reply': "🛒 Your cart is empty!\n\nBrowse our products and click **Add to Cart** to get started."})
        total = sum(i.product.price * i.qty for i in items)
        lines = '\n'.join(f"• {i.product.name} × {i.qty} = ₹{i.product.price * i.qty:,.0f}" for i in items)
        return Response({'reply': f"🛒 Your cart has {items.count()} item(s):\n\n{lines}\n\n💰 Total: ₹{total:,.0f}"})

    # ── Orders ──
    if re.search(r'order|purchase|bought|my order', msg):
        if not user:
            return Response({'reply': "🔒 Please login to view your orders."})
        orders = Order.objects.filter(user=user).order_by('-created_at')[:3]
        if not orders.exists():
            return Response({'reply': "📦 You haven't placed any orders yet.\n\nStart shopping and place your first order!"})
        lines = '\n'.join(f"• Order #{o.id} — ₹{o.total:,.0f} — {o.status.capitalize()}" for o in orders)
        return Response({'reply': f"📦 Your recent orders:\n\n{lines}\n\nFor more details, contact our support."})

    # ── Delivery ──
    if re.search(r'deliver|shipping|dispatch|when.*arrive|how long', msg):
        return Response({'reply': "🚚 Delivery Information:\n\n• 📍 We deliver all across India\n• ⏱️ Standard delivery: 3–5 business days\n• ⚡ Express delivery: 1–2 business days\n• 🆓 Free delivery on orders above ₹999\n• 📦 Orders are dispatched within 24 hours"})

    # ── Payment ──
    if re.search(r'payment|pay|upi|cod|cash|gpay|phonepe|paytm', msg):
        return Response({'reply': "💳 We accept the following payment methods:\n\n📲 **UPI** — Google Pay, PhonePe, Paytm, BHIM UPI\n💵 **Cash on Delivery (COD)** — Pay at your doorstep\n\nAll transactions are 100% secure! 🛡️"})

    # ── Return / refund ──
    if re.search(r'return|refund|exchange|replace|cancel', msg):
        return Response({'reply': "↩️ Return & Refund Policy:\n\n• 7-day easy return policy\n• Full refund for damaged/defective items\n• Refund processed within 5–7 business days\n• Contact support with your Order ID to initiate a return"})

    # ── Discount / offer ──
    if re.search(r'discount|offer|coupon|promo|deal|sale', msg):
        return Response({'reply': "🎉 Current Offers at AnixCart:\n\n• 🆓 Free delivery on orders above ₹999\n• 💥 Up to 30% off on Electronics\n• 🎧 Special deals on Audio products\n\nKeep checking back — new offers every week!"})

    # ── Stock ──
    if re.search(r'stock|available|in stock|out of stock', msg):
        out = Product.objects.filter(stock=0).count()
        low = Product.objects.filter(stock__gt=0, stock__lte=5).count()
        ok = Product.objects.filter(stock__gt=5).count()
        return Response({'reply': f"📊 Current Stock Status:\n\n✅ In Stock: {ok} products\n⚠️ Low Stock: {low} products\n❌ Out of Stock: {out} products\n\nOrder soon before items run out!"})

    # ── Contact / support ──
    if re.search(r'contact|support|help|email|phone|number|call', msg):
        return Response({'reply': "📞 AnixCart Support:\n\n📧 Email: support@anixcart.com\n📱 Phone: +91 98765 43210\n⏰ Hours: Mon–Sat, 9 AM – 6 PM\n\nWe typically respond within 2 hours!"})

    # ── About ──
    if re.search(r'about|who are you|anixcart|what is this', msg):
        return Response({'reply': "🛒 About AnixCart:\n\nAnixCart is your one-stop online shop for premium electronics, audio gear, accessories, wearables and peripherals — all at the best prices in India!\n\n🇮🇳 Made with ❤️ in India"})

    # ── Thanks ──
    if re.search(r'thank|thanks|thx|ty|great|awesome|nice', msg):
        return Response({'reply': "😊 You're welcome! Happy shopping at AnixCart 🛒\n\nIs there anything else I can help you with?"})

    # ── Bye ──
    if re.search(r'bye|goodbye|see you|cya|exit', msg):
        return Response({'reply': "👋 Goodbye! Thanks for visiting AnixCart.\n\nHappy shopping! Come back soon 🛍️"})

    # ── Fallback ──
    return Response({'reply': "🤔 I'm not sure about that. Here's what I can help with:\n\n• 🛍️ Browse products & categories\n• 💰 Check prices\n• 🛒 View your cart\n• 📦 Track your orders\n• 🚚 Delivery info\n• 💳 Payment methods\n• ↩️ Returns & refunds\n\nTry asking something like *'show me audio products'* or *'what are your cheapest items'*!"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    address = request.data.get('address', '').strip()
    payment_method = request.data.get('payment_method')
    upi_app = request.data.get('upi_app', '')
    upi_id = request.data.get('upi_id', '')

    if not address:
        return Response({'error': 'Delivery address is required'}, status=400)
    if payment_method not in ['upi', 'cod']:
        return Response({'error': 'Invalid payment method'}, status=400)
    if payment_method == 'upi' and not upi_id.strip():
        return Response({'error': 'UPI ID is required'}, status=400)

    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        return Response({'error': 'Cart is empty'}, status=400)

    total = sum(item.product.price * item.qty for item in cart_items)

    order = Order.objects.create(
        user=request.user,
        address=address,
        payment_method=payment_method,
        upi_app=upi_app,
        upi_id=upi_id,
        total=total,
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            price=item.product.price,
            qty=item.qty,
        )

    cart_items.delete()
    return Response(OrderSerializer(order).data, status=201)

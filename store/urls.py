from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ProductViewSet, signup, cart_list, cart_add, cart_remove, cart_clear, place_order, chatbot

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', signup),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('cart/', cart_list),
    path('cart/add/', cart_add),
    path('cart/remove/<int:item_id>/', cart_remove),
    path('cart/clear/', cart_clear),
    path('orders/place/', place_order),
    path('chatbot/', chatbot),
]

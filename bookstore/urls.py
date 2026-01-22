from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# ✅ IMPORT VIEWS CORRECTLY FROM store APP
from store import views
from store.views import (
    home,
    add_to_cart,
    view_cart,
    increase_qty,
    decrease_qty,
    remove_from_cart,
    checkout,
    payment,
    order_success,
    signup_view,
    login_view,
    logout_view,
    profile,
    book_detail,
)

urlpatterns = [
    # ---------------- ADMIN ----------------
    path('admin/', admin.site.urls),

    # ---------------- HOME ----------------
    path('', home, name='home'),

    # ---------------- BOOK DETAIL ----------------
    path('book/<int:book_id>/', book_detail, name='book_detail'),

    # ---------------- CART ----------------
    path('add-to-cart/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/increase/<int:book_id>/', increase_qty, name='increase_qty'),
    path('cart/decrease/<int:book_id>/', decrease_qty, name='decrease_qty'),
    path('cart/remove/<int:book_id>/', remove_from_cart, name='remove_from_cart'),

    # ---------------- CHECKOUT & PAYMENT ----------------
    path('checkout/', checkout, name='checkout'),
    path('payment/', payment, name='payment'),
    path('order-success/', order_success, name='order_success'),

    # ---------------- AUTH ----------------
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # ---------------- PROFILE ----------------
    path('profile/', profile, name='profile'),

    # ---------------- WISHLIST ❤️ ----------------
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    path('address/edit/', views.edit_address, name='edit_address'),


]

# ---------------- MEDIA FILES ----------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

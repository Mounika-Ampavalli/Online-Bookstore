from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import (
    Book,
    Order,
    OrderItem,
    Wishlist,
    Address,
)

# ================= HOME =================
# ================= HOME =================
def home(request):
    query = request.GET.get('q')
    selected_category = request.GET.get('category')

    books = Book.objects.all()

    # 🔍 SEARCH FILTER
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )

    # 📚 CATEGORY FILTER
    if selected_category:
        books = books.filter(category=selected_category)

    # 🧾 CART COUNT
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    # 📂 SIDEBAR CATEGORIES
    categories = Book.objects.values_list(
        'category', flat=True
    ).distinct().order_by('category')

    return render(request, 'store/home.html', {
        'books': books,
        'cart_count': cart_count,
        'categories': categories,
        'selected_category': selected_category
    })

# ================= ADD TO CART =================
def add_to_cart(request, book_id):
    cart = request.session.get('cart', {})
    book_id = str(book_id)

    cart[book_id] = cart.get(book_id, 0) + 1
    request.session['cart'] = cart

    messages.success(request, "Book added to cart")

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('home')



# ================= CART =================
def view_cart(request):
    cart = request.session.get('cart', {})
    books = Book.objects.filter(id__in=cart.keys())

    cart_items = []
    total_price = 0

    for book in books:
        qty = cart[str(book.id)]
        subtotal = book.price * qty
        total_price += subtotal

        cart_items.append({
            'book': book,
            'qty': qty,
            'subtotal': subtotal
        })

    cart_count = sum(cart.values())

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': cart_count
    })


def increase_qty(request, book_id):
    cart = request.session.get('cart', {})
    book_id = str(book_id)

    if book_id in cart:
        cart[book_id] += 1

    request.session['cart'] = cart
    return redirect('view_cart')


def decrease_qty(request, book_id):
    cart = request.session.get('cart', {})
    book_id = str(book_id)

    if book_id in cart:
        cart[book_id] -= 1
        if cart[book_id] <= 0:
            del cart[book_id]

    request.session['cart'] = cart
    return redirect('view_cart')


def remove_from_cart(request, book_id):
    cart = request.session.get('cart', {})
    book_id = str(book_id)

    if book_id in cart:
        del cart[book_id]

    request.session['cart'] = cart
    return redirect('view_cart')


# ================= CHECKOUT =================
@login_required(login_url='login')
def checkout(request):
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    books = Book.objects.filter(id__in=cart.keys())
    total_price = sum(book.price * cart[str(book.id)] for book in books)

    return render(request, 'store/checkout.html', {
        'total_price': total_price,
        'cart_count': cart_count
    })


@login_required(login_url='login')
def payment(request):
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    if not cart:
        return redirect('home')

    books = Book.objects.filter(id__in=cart.keys())
    total_price = sum(book.price * cart[str(book.id)] for book in books)

    # ================= FROM CHECKOUT =================
    if request.method == "POST" and request.POST.get("from_checkout"):
        request.session['address_data'] = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
        }
        return redirect('payment')

    # ================= SHOW PAYMENT PAGE =================
    if request.method == "GET":
        return render(request, 'store/payment.html', {
            'total_price': total_price,
            'cart_count': cart_count
        })

    # ================= CONFIRM PAYMENT =================
    if request.method == "POST" and request.POST.get("confirm_payment"):
        address = request.session.get('address_data')

        if not address:
            return redirect('checkout')

        Address.objects.update_or_create(
    user=request.user,
    defaults={
        'full_name': request.POST.get('name') or request.user.username,
        'email': request.POST.get('email') or request.user.email,
        'phone': request.POST.get('phone') or '',
        'address': request.POST.get('address') or '',
    }
)


        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )

        for book in books:
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=cart[str(book.id)]
            )

        # 🔥 THIS WAS MISSING EARLIER
        request.session['cart'] = {}
        request.session.modified = True
        request.session.pop('address_data', None)

        return redirect('order_success')

    return redirect('checkout')



# ================= ORDER SUCCESS =================
@login_required(login_url='login')
def order_success(request):
    return render(request, 'store/order_success.html')


# ================= PROFILE =================
@login_required(login_url='login')
def profile(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related('items__book')
        .order_by('-created_at')
    )

    wishlist_items = Wishlist.objects.filter(user=request.user)
    address = Address.objects.filter(user=request.user).first()

    return render(request, 'store/profile.html', {
        'orders': orders,
        'wishlist_items': wishlist_items,
        'address': address
    })


# ================= BOOK DETAIL =================
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user,
            book=book
        ).exists()

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    return render(request, 'store/book_detail.html', {
        'book': book,
        'in_wishlist': in_wishlist,
        'cart_count': cart_count
    })


# ================= WISHLIST =================
@login_required(login_url='login')
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.get_or_create(user=request.user, book=book)
    messages.success(request, "Added to wishlist ❤️")
    return redirect('book_detail', book_id=book.id)
# ================= REMOVE FROM WISHLIST =================
@login_required(login_url='login')
def remove_from_wishlist(request, book_id):
    Wishlist.objects.filter(
        user=request.user,
        book_id=book_id
    ).delete()
    messages.success(request, "Removed from wishlist")
    return redirect('profile')


# ================= AUTH =================
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'store/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid credentials")
        return redirect('login')

    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')
@login_required(login_url='login')
def edit_address(request):
    if request.method == "POST":
        Address.objects.update_or_create(
            user=request.user,
            defaults={
                'full_name': request.POST.get('full_name'),
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'address': request.POST.get('address'),
            }
        )
        messages.success(request, "Address updated successfully")
    return redirect('profile')

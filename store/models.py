from django.db import models
from django.contrib.auth.models import User


# ================= BOOK MODEL =================
class Book(models.Model):

    CATEGORY_CHOICES = [
        ('Programming', 'Programming'),
        ('Fiction', 'Fiction'),
        ('Non fiction', 'Non fiction'),
        ('Technology', 'Technology'),
        ('Education', 'Education'),
        ('Science', 'Science'),
        ('General', 'General'),
        ('Love', 'Love'),
        ('Biography', 'Biography'),
        ('Horror', 'Horror'),
        ('Romantic', 'Romantic'),
        ('Self-help', 'Self-help'),
        ('Storytelling', 'Storytelling'),
        ('Children', 'Children'),
        ('Competitive', 'Competitive'),
        ('Psychology', 'Psychology'),
        ('Motivational', 'Motivational'),
        ('Fantasy', 'Fantasy'),
        ('Novels', 'Novels'),
        ('History', 'History'),
        ('Biography', 'Biography'),
        ('Comics', 'Comics'),
        ('Self-help', 'Self-help'),
        ('Poetry', 'Poetry'),
        ('Thriller/Mystery', 'Thriller/Mystery'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='General'
    )

    description = models.TextField(blank=True)

    def __str__(self):
        return self.title



# ================= WISHLIST MODEL =================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


# ================= ORDER =================
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, default="Placed")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"
    

# ================= ORDER ITEMS (THIS FIXES IMAGES) =================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} (x{self.quantity})"


# ================= USER ADDRESS =================
class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f"{self.user.username} Address"


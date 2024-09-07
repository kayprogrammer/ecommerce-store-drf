from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.core.validators import MaxValueValidator, MinValueValidator
from autoslug import AutoSlugField
from django.conf import settings
from apps.accounts.models import GuestUser, User
from apps.common.models import BaseModel, IsDeletedModel, generate_unique_code
from apps.shop.choices import (
    DELIVERY_STATUS_CHOICES,
    PAYMENT_GATEWAY_CHOICES,
    PAYMENT_STATUS_CHOICES,
    RATING_CHOICES,
)

CATEGORY_IMAGE_PREFIX = "category_images/"
PRODUCT_IMAGE_PREFIX = "product_images/"


class Size(BaseModel):
    """
    Represents a size attribute for products.

    Attributes:
        value (str): The size value, unique for each instance.

    Methods:
        __str__():
            Returns the string representation of the size value.
    """

    value = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return str(self.value)


class Color(BaseModel):
    """
    Represents a color attribute for products.

    Attributes:
        value (str): The color value, unique for each instance.

    Methods:
        __str__():
            Returns the string representation of the color value.
    """

    value = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return str(self.value)


class Category(BaseModel):
    """
    Represents a product category.

    Attributes:
        name (str): The category name, unique for each instance.
        slug (str): The slug generated from the name, used in URLs.
        image (ImageField): An image representing the category.

    Methods:
        __str__():
            Returns the string representation of the category name.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)
    image = models.ImageField(upload_to=CATEGORY_IMAGE_PREFIX)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Categories"


class Country(BaseModel):
    """
    Represents a country with its associated details.

    Attributes:
        name (str): The name of the country, unique for each instance.
        code (str): The country code, unique for each instance.
        phone_code (str): The international phone code for the country.

    Methods:
        __str__():
            Returns the string representation of the country name.
    """

    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    phone_code = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Countries"


class Product(IsDeletedModel):
    """
    Represents a product listed for sale.

    Attributes:
        seller (ForeignKey): The user who is selling the product.
        name (str): The name of the product.
        slug (str): The slug generated from the name, used in URLs.
        desc (str): A description of the product.
        price_old (Decimal): The original price of the product.
        price_current (Decimal): The current price of the product.
        category (ForeignKey): The category to which the product belongs.
        sizes (ManyToManyField): The available sizes for the product.
        colors (ManyToManyField): The available colors for the product.
        in_stock (int): The quantity of the product in stock.
        image1 (ImageField): The first image of the product.
        image2 (ImageField): The second image of the product.
        image3 (ImageField): The third image of the product.

    Properties:
        image1_url (str): The URL of the first image.
        image2_url (str): The URL of the second image.
        image3_url (str): The URL of the third image.
        default_size (Size): The default size of the product.
        default_color (Color): The default color of the product.

    Methods:
        return_img_url(image: ImageFieldFile):
            Returns the URL of the given image field or None if not available.
    """

    seller = models.ForeignKey(
        "sellers.Seller", on_delete=models.SET_NULL, related_name="products", null=True
    )
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)
    desc = models.TextField()
    price_old = models.DecimalField(max_digits=10, decimal_places=2)
    price_current = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    sizes = models.ManyToManyField(Size, related_name="products", blank=True)
    colors = models.ManyToManyField(Color, related_name="products", blank=True)
    in_stock = models.IntegerField(default=5)

    # Only 3 images are allowed
    image1 = models.ImageField(upload_to=PRODUCT_IMAGE_PREFIX)
    image2 = models.ImageField(upload_to=PRODUCT_IMAGE_PREFIX, blank=True)
    image3 = models.ImageField(upload_to=PRODUCT_IMAGE_PREFIX, blank=True)

    def return_img_url(self, image: ImageFieldFile):
        try:
            url = image.url
        except:
            url = None
        return url

    @property
    def image1_url(self):
        return self.return_img_url(self.image1)

    @property
    def image2_url(self):
        return self.return_img_url(self.image2)

    @property
    def image3_url(self):
        return self.return_img_url(self.image3)

    def __str__(self):
        return str(self.name)


class Wishlist(BaseModel):
    """
    Represents a wishlist item for a user or guest.

    Attributes:
        user (ForeignKey): The user who owns the wishlist item.
        product (ForeignKey): The product added to the wishlist.
        guest (ForeignKey): The guest user who owns the wishlist item.

    Meta:
        unique constraints:
            unique_user_product_wishlist_item: Ensures that a user cannot have duplicate products in their wishlist.
            unique_guest_product_wishlist_item: Ensures that a guest cannot have duplicate products in their wishlist.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist", null=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlist"
    )
    guest = models.ForeignKey(
        GuestUser, on_delete=models.CASCADE, related_name="wishlist", null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_wishlist_item",
            ),
            models.UniqueConstraint(
                fields=["guest", "product"],
                name="unique_guest_product_wishlist_item",
            ),
        ]


class ShippingAddress(BaseModel):
    """
    Represents a shipping address associated with a user.

    Attributes:
        user (ForeignKey): The user who owns the shipping address.
        full_name (str): The full name of the recipient.
        email (str): The email address of the recipient.
        phone (str): The phone number of the recipient.
        address (str): The street address of the recipient.
        city (str): The city of the recipient.
        state (str): The state of the recipient.
        country (ForeignKey): The country of the recipient.
        zipcode (int): The postal code of the recipient.

    Methods:
        __str__():
            Returns a string representation of the shipping details.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shipping_addresses"
    )
    full_name = models.CharField(max_length=1000)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    zipcode = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.full_name}'s shipping details"


class Coupon(BaseModel):
    """
    Represents a discount coupon.

    Attributes:
        code (str): The unique coupon code.
        expiry_date (DateTime): The expiry date of the coupon.
        percentage_off (int): The percentage discount offered by the coupon.

    Methods:
        save(*args, **kwargs):
            Overrides the save method to generate a unique coupon code when a new coupon is created.
    """

    code = models.CharField(max_length=12, blank=True, unique=True)
    expiry_date = models.DateTimeField(null=True)
    percentage_off = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            self.code = generate_unique_code(Coupon, "code")
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.code)


class Order(IsDeletedModel):
    """
    Represents a customer's order.

    Attributes:
        user (ForeignKey): The user who placed the order.
        tx_ref (str): The unique transaction reference.
        delivery_status (str): The delivery status of the order.
        payment_status (str): The payment status of the order.
        payment_gateway (str): The payment gateway used for the order.

    Methods:
        __str__():
            Returns a string representation of the transaction reference.
        save(*args, **kwargs):
            Overrides the save method to generate a unique transaction reference when a new order is created.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    tx_ref = models.CharField(max_length=100, blank=True, unique=True)
    delivery_status = models.CharField(
        max_length=20, default="PENDING", choices=DELIVERY_STATUS_CHOICES
    )
    payment_status = models.CharField(
        max_length=20, default="PENDING", choices=PAYMENT_STATUS_CHOICES
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_GATEWAY_CHOICES, null=True
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    date_delivered = models.DateTimeField(null=True, blank=True)

    # Shipping address details
    full_name = models.CharField(max_length=1000, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=100, null=True)
    zipcode = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user.full_name}'s order"

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            self.tx_ref = generate_unique_code(Order, "tx_ref")
        super().save(*args, **kwargs)

    @property
    def get_cart_subtotal(self):
        orderitems = self.orderitems.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def shipping_fee(self):
        return settings.SHIPPING_FEE * len(self.orderitems.all())

    @property
    def get_cart_total(self):
        coupon = self.coupon
        total = self.get_cart_subtotal + self.shipping_fee
        if coupon:
            total = total - ((coupon.percentage_off * total) / 100)
        return total

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "coupon"], name="unique_user_coupon_order"
            )
        ]


class OrderItem(BaseModel):
    """
    Represents an item within an order.

    Attributes:
        order (ForeignKey): The order to which this item belongs.
        product (ForeignKey): The product associated with this order item.
        quantity (int): The quantity of the product ordered.
        color (ForeignKey): The color chosen for this order item.
        size (ForeignKey): The size chosen for this order item.

    Meta:
        unique constraints:
            unique_user_product_order_orderitems: Ensures that a user cannot have duplicate items with the same product, color, and size.
            unique_guest_product_order_orderitems: Ensures that a guest user cannot have duplicate items with the same product, color, and size.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest = models.ForeignKey(
        GuestUser, on_delete=models.CASCADE, null=True, blank=True
    )
    order = models.ForeignKey(
        Order,
        related_name="orderitems",
        null=True,
        on_delete=models.CASCADE,
        blank=True,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.ForeignKey(
        Size, on_delete=models.CASCADE, related_name="orderitems", null=True
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, related_name="orderitems", null=True
    )

    @property
    def get_total(self):
        return self.product.price_current * self.quantity

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "product",
                    "order",
                    "size",
                    "color",
                ],
                name="unique_user_product_order_orderitems",
                condition=models.Q(order__isnull=False),
            ),
            models.UniqueConstraint(
                fields=[
                    "user",
                    "product",
                    "size",
                    "color",
                ],
                name="unique_user_product_orderitems",
                condition=models.Q(order__isnull=True),
            ),
            models.UniqueConstraint(
                fields=[
                    "guest",
                    "product",
                    "order",
                    "size",
                    "color",
                ],
                condition=models.Q(order__isnull=False),
                name="unique_guest_product_order_orderitems",
            ),
            models.UniqueConstraint(
                fields=[
                    "guest",
                    "product",
                    "size",
                    "color",
                ],
                condition=models.Q(order__isnull=True),
                name="unique_guest_product_orderitems",
            ),
        ]

    def __str__(self):
        return str(self.product.name)

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.quantity == 0:
                # Ensure to make it one just incase it's creating and the user sets 0
                self.quantity = 1
        return super(OrderItem, self).save(*args, **kwargs)


class Review(BaseModel):
    """
    Represents a product review given by a user.

    Attributes:
        user (ForeignKey): The user who provided the review.
        product (ForeignKey): The product being reviewed.
        rating (int): The rating provided for the product.
        text (str): The comment provided by the user.

    Meta:
        unique constraints:
            unique_user_product_reviews: Ensures that a user cannot review the same product more than once.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.TextField()

    def __str__(self):
        return f"{self.user.full_name}----{self.product.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_reviews",
            ),
        ]

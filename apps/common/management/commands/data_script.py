from typing import List
from pathlib import Path
from django.conf import settings
from django.utils.text import slugify
from django.db import transaction
from apps.accounts.models import User
from apps.common.management.commands.seed import (
    COUNTRIES_DATA,
    PRODUCT_CATEGORIES,
    PRODUCT_DATA,
    REVIEWS,
    SIZES_DATA,
    COLOUR_DATA,
)

from apps.shop.choices import RATING_CHOICES
from apps.shop.models import (
    CATEGORY_IMAGE_PREFIX,
    PRODUCT_IMAGE_PREFIX,
    Category,
    Country,
    Product,
    Review,
    Size,
    Color,
)
from cloudinary_storage.storage import MediaCloudinaryStorage
import os, random

CURRENT_DIR = Path(__file__).resolve().parent
test_images_directory = os.path.join(CURRENT_DIR, "images")
test_category_images_directory = f"{test_images_directory}/categories"
test_product_images_directory = f"{test_images_directory}/products"


class CreateData(object):
    def __init__(self) -> None:
        admin = self.create_superuser()
        reviewer = self.create_reviewer()
        self.create_countries()
        self.create_categories()
        sizes, colors = self.create_sizes_and_colors()
        products = self.create_products(admin, sizes, colors)
        self.create_reviews(admin, reviewer, products)

    def create_superuser(self) -> User:
        user_dict = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
            "is_superuser": True,
            "is_staff": True,
        }
        superuser = User.objects.get_or_none(email=user_dict["email"])
        if not superuser:
            superuser = User.objects.create_user(**user_dict)
        return superuser

    def create_reviewer(self) -> User:
        user_dict = {
            "first_name": "Test",
            "last_name": "Reviewer",
            "email": settings.FIRST_REVIEWER_EMAIL,
            "password": settings.FIRST_REVIEWER_PASSWORD,
        }
        reviewer = User.objects.get_or_none(email=user_dict["email"])
        if not reviewer:
            reviewer = User.objects.create_user(**user_dict)
        return reviewer

    def create_countries(self):
        if Country.objects.exists():
            return
        country_instances = [
            Country(
                name=country["name"],
                code=country["code"],
                phone_code=country["phone_code"],
            )
            for country in COUNTRIES_DATA
        ]
        Country.objects.bulk_create(country_instances)

    def get_image(self, images_list, substring):
        return next((s for s in images_list if s.startswith(substring)), None)

    def create_categories(self):
        categories_exists = Category.objects.exists()
        if not categories_exists:
            images = os.listdir(test_category_images_directory)
            categories_to_create = []
            for category_name in PRODUCT_CATEGORIES:
                with transaction.atomic():
                    slug = slugify(category_name)
                    image_file_name = self.get_image(images, slug)
                    image_path = os.path.join(
                        test_category_images_directory, image_file_name
                    )
                    with open(image_path, "rb") as image_file:
                        file_storage = MediaCloudinaryStorage()
                        file_path = file_storage.save(
                            f"{CATEGORY_IMAGE_PREFIX}{image_file_name}", image_file
                        )
                        category = Category(
                            name=category_name, slug=slug, image=file_path
                        )
                        categories_to_create.append(category)
            Category.objects.bulk_create(categories_to_create)

    def create_sizes_and_colors(self):
        sizes = Size.objects.all()
        colors = Color.objects.all()
        if not sizes.exists():
            sizes_to_create = [Size(value=size) for size in SIZES_DATA]
            Size.objects.bulk_create(sizes_to_create)
        if not colors.exists():
            colors_to_create = [Color(value=colour) for colour in COLOUR_DATA]
            Color.objects.bulk_create(colors_to_create)
        return sizes, colors

    def create_products(self, admin, sizes, colors):
        products = Product.objects.all()
        if not products.exists():
            with transaction.atomic():
                images = os.listdir(test_product_images_directory)
                products_to_create = []
                for idx, product_data in enumerate(PRODUCT_DATA):
                    category_slug = product_data["category_slug"]
                    category = Category.objects.get_or_none(slug=category_slug)
                    if not category:
                        pass
                    image_file_name = self.get_image(images, category_slug)
                    image_path = os.path.join(
                        test_product_images_directory, image_file_name
                    )
                    with open(image_path, "rb") as image_file:
                        file_storage = MediaCloudinaryStorage()
                        file_path = file_storage.save(
                            f"{PRODUCT_IMAGE_PREFIX}{image_file_name}", image_file
                        )
                        product = Product(
                            seller=admin,
                            name=product_data["name"],
                            category=category,
                            desc="This is a good product you'll never regret. It is of good quality",
                            price_old=(idx + 1) * 5000,
                            price_current=(idx + 1) * 4000,
                            image1=file_path,
                        )
                        products_to_create.append(product)
                products = Product.objects.bulk_create(products_to_create)

                # Product update sizes and colors
                for product in products:
                    product.sizes.set(sizes)
                    product.colors.set(colors)
        return products

    def create_reviews(self, admin: User, reviewer: User, products: List[Product]):
        reviews_exists = Review.objects.exists()
        rating_choices = [r[0] for r in RATING_CHOICES]
        if not reviews_exists:
            reviews_to_create = []
            for product in products:
                rev1 = Review(
                    product=product,
                    user=admin,
                    text=REVIEWS[0],
                    rating=random.choice(rating_choices),
                )
                rev2 = Review(
                    product=product,
                    user=reviewer,
                    text=random.choice(REVIEWS[1:]),
                    rating=random.choice(rating_choices),
                )
                reviews_to_create.extend([rev1, rev2])
            Review.objects.bulk_create(reviews_to_create)

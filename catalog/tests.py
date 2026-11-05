from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, Product


class CatalogFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Видеокарты", slug="videokarty")
        self.product = Product.objects.create(
            name="RTX 4070",
            category=self.category,
            price=Decimal("425000"),
            in_stock=True,
        )

    def test_catalog_and_filters(self):
        response = self.client.get(reverse("product_list"), {"category": "videokarty", "in_stock": "1"})
        self.assertContains(response, "RTX 4070")

    def test_add_to_cart_and_checkout(self):
        add = self.client.post(reverse("add_to_cart", args=[self.product.pk]), {"qty": "2", "next": "/"})
        self.assertEqual(add.status_code, 302)
        cart = self.client.get(reverse("cart"))
        self.assertContains(cart, "RTX 4070")

        checkout = self.client.post(
            reverse("checkout"),
            {"name": "Али", "phone": "+77001234567", "email": "ali@example.com", "comment": ""},
        )
        self.assertEqual(checkout.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, Decimal("850000"))
        self.assertEqual(self.client.session.get("cart"), {})

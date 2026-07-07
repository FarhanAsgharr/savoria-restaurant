"""Integration tests for the REST API endpoints."""

from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from menu.models import Category, MenuItem, Order


class CategoryAPITests(APITestCase):
    def setUp(self):
        self.active = Category.objects.create(name="Starters", display_order=1)
        self.inactive = Category.objects.create(name="Hidden", display_order=2, is_active=False)
        MenuItem.objects.create(category=self.active, name="Soup", price=Decimal("6.00"))
        MenuItem.objects.create(
            category=self.active,
            name="Off menu",
            price=Decimal("6.00"),
            is_available=False,
        )

    def test_list_returns_only_active_categories(self):
        res = self.client.get("/api/categories/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [c["name"] for c in res.data["results"]]
        self.assertIn("Starters", names)
        self.assertNotIn("Hidden", names)

    def test_item_count_reflects_available_items_only(self):
        res = self.client.get("/api/categories/starters/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only the available "Soup" counts, not the unavailable item.
        self.assertEqual(res.data["item_count"], 1)

    def test_detail_by_slug(self):
        res = self.client.get("/api/categories/starters/")
        self.assertEqual(res.data["slug"], "starters")

    def test_missing_category_returns_404(self):
        res = self.client.get("/api/categories/nope/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class MenuItemAPITests(APITestCase):
    def setUp(self):
        self.starters = Category.objects.create(name="Starters")
        self.mains = Category.objects.create(name="Mains")
        self.cheap = MenuItem.objects.create(
            category=self.starters, name="Bruschetta", price=Decimal("8.00")
        )
        self.pricey = MenuItem.objects.create(
            category=self.mains, name="Lobster", price=Decimal("45.00")
        )
        self.sold_out = MenuItem.objects.create(
            category=self.mains,
            name="Truffle Pasta",
            price=Decimal("30.00"),
            is_available=False,
        )

    def test_list_is_paginated(self):
        res = self.client.get("/api/items/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, res.data)

    def test_filter_by_category_slug(self):
        res = self.client.get("/api/items/?category=mains")
        names = [i["name"] for i in res.data["results"]]
        self.assertCountEqual(names, ["Lobster", "Truffle Pasta"])

    def test_filter_by_availability(self):
        res = self.client.get("/api/items/?is_available=true")
        names = [i["name"] for i in res.data["results"]]
        self.assertNotIn("Truffle Pasta", names)

    def test_search_matches_name(self):
        res = self.client.get("/api/items/?search=lobster")
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["name"], "Lobster")

    def test_ordering_by_price_ascending(self):
        res = self.client.get("/api/items/?ordering=price")
        prices = [Decimal(i["price"]) for i in res.data["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_detail_includes_category_metadata(self):
        res = self.client.get("/api/items/bruschetta/")
        self.assertEqual(res.data["category_name"], "Starters")
        self.assertEqual(res.data["category_slug"], "starters")


class OrderAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Mains")
        self.steak = MenuItem.objects.create(
            category=self.category, name="Steak", price=Decimal("30.00")
        )
        self.fish = MenuItem.objects.create(
            category=self.category, name="Fish", price=Decimal("20.00")
        )
        self.unavailable = MenuItem.objects.create(
            category=self.category,
            name="Special",
            price=Decimal("50.00"),
            is_available=False,
        )

    def _payload(self, items):
        return {
            "customer_name": "Ada Lovelace",
            "customer_phone": "+15551234567",
            "address": "1 Main St",
            "items": items,
        }

    def test_create_order_computes_total_server_side(self):
        payload = self._payload(
            [
                {"menu_item": self.steak.id, "quantity": 2},
                {"menu_item": self.fish.id, "quantity": 1},
            ]
        )
        res = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["total_amount"], "80.00")
        self.assertEqual(Order.objects.count(), 1)

    def test_unit_price_is_snapshotted_from_db_not_client(self):
        # Even if a client tried to send a price, it is ignored.
        payload = self._payload([{"menu_item": self.steak.id, "quantity": 1}])
        payload["items"][0]["unit_price"] = "0.01"  # malicious/ignored field
        res = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["order_items"][0]["unit_price"], "30.00")

    def test_empty_items_rejected(self):
        res = self.client.post("/api/orders/", self._payload([]), format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_phone_and_address_rejected(self):
        payload = {
            "customer_name": "No Contact",
            "items": [{"menu_item": self.steak.id, "quantity": 1}],
        }
        res = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer_phone", res.data)
        self.assertIn("address", res.data)

    def test_unavailable_item_rejected(self):
        payload = self._payload([{"menu_item": self.unavailable.id, "quantity": 1}])
        res = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_order(self):
        payload = self._payload([{"menu_item": self.steak.id, "quantity": 1}])
        created = self.client.post("/api/orders/", payload, format="json")
        order_id = created.data["id"]
        res = self.client.get(f"/api/orders/{order_id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["customer_name"], "Ada Lovelace")

    def test_order_list_not_exposed(self):
        # Listing all orders must not be publicly available.
        res = self.client.get("/api/orders/")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

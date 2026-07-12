"""
Seed realistic demo orders spread over the past month, with a mix of
statuses (delivered, cancelled, confirmed, etc.) so every admin section has
data and the per-status counts look real.

Usage:
    python manage.py seed_orders                # ~45 orders over ~35 days
    python manage.py seed_orders --count 60 --days 40
    python manage.py seed_orders --flush        # delete existing orders first
"""

from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from menu.models import MenuItem, Order, OrderItem

# Lahore-only delivery areas with representative coordinates.
LAHORE_AREAS = [
    ("DHA Phase 5, Lahore", 31.4697, 74.4126),
    ("Gulberg III, Lahore", 31.5169, 74.3484),
    ("Model Town, Lahore", 31.4847, 74.3266),
    ("Johar Town, Lahore", 31.4697, 74.2728),
    ("Bahria Town, Lahore", 31.3684, 74.1817),
    ("Cantt, Lahore", 31.5497, 74.3936),
    ("Iqbal Town, Lahore", 31.5100, 74.2900),
    ("Faisal Town, Lahore", 31.4800, 74.3100),
    ("Wapda Town, Lahore", 31.4300, 74.2600),
    ("Garden Town, Lahore", 31.5030, 74.3200),
]

FIRST_NAMES = [
    "Ali",
    "Ayesha",
    "Bilal",
    "Fatima",
    "Hamza",
    "Sana",
    "Usman",
    "Zainab",
    "Ahmed",
    "Hira",
    "Saad",
    "Maryam",
    "Hassan",
    "Iqra",
    "Umar",
    "Noor",
]
LAST_NAMES = [
    "Khan",
    "Malik",
    "Ahmed",
    "Butt",
    "Sheikh",
    "Raza",
    "Iqbal",
    "Tariq",
    "Hussain",
    "Chaudhry",
    "Farooq",
    "Siddiqui",
]

# Weighted status mix — delivered dominates so the history looks realistic.
STATUS_WEIGHTS = [
    (Order.Status.DELIVERED, 50),
    (Order.Status.CANCELLED, 12),
    (Order.Status.CONFIRMED, 12),
    (Order.Status.PREPARING, 8),
    (Order.Status.READY, 7),
    (Order.Status.OUT_FOR_DELIVERY, 6),
    (Order.Status.PENDING, 5),
]


class Command(BaseCommand):
    help = "Seed realistic demo orders spread over the past month."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=45)
        parser.add_argument("--days", type=int, default=35)
        parser.add_argument("--flush", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            Order.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing orders deleted."))
        elif Order.objects.exists():
            self.stdout.write("Orders already exist — skipping (use --flush to reseed).")
            return

        items = list(MenuItem.objects.filter(is_available=True))
        if not items:
            self.stderr.write("No available menu items — run seed_menu first.")
            return

        statuses = [s for s, _ in STATUS_WEIGHTS]
        weights = [w for _, w in STATUS_WEIGHTS]
        count = options["count"]
        days = options["days"]
        now = timezone.now()
        created = 0

        for _ in range(count):
            area, lat, lng = random.choice(LAHORE_AREAS)
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            phone = f"+9230{random.randint(0, 9)}{random.randint(1000000, 9999999)}"
            status = random.choices(statuses, weights=weights, k=1)[0]

            # A random moment within the past `days` days.
            placed = now - timedelta(
                days=random.randint(0, days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            order = Order.objects.create(
                customer_name=name,
                customer_phone=phone,
                address=f"House {random.randint(1, 400)}, {area}",
                latitude=Decimal(str(round(lat + random.uniform(-0.01, 0.01), 6))),
                longitude=Decimal(str(round(lng + random.uniform(-0.01, 0.01), 6))),
                status=status,
            )

            total = Decimal("0.00")
            lines = []
            for it in random.sample(items, k=random.randint(1, min(4, len(items)))):
                qty = random.randint(1, 3)
                lines.append(
                    OrderItem(
                        order=order,
                        menu_item=it,
                        menu_item_name=it.name,
                        quantity=qty,
                        unit_price=it.price,
                    )
                )
                total += it.price * qty
            OrderItem.objects.bulk_create(lines)

            # Backdate timestamps (created_at is auto_now_add, so update directly).
            delivered = (
                placed + timedelta(hours=random.randint(1, 6))
                if status == Order.Status.DELIVERED
                else None
            )
            Order.objects.filter(pk=order.pk).update(
                total_amount=total, created_at=placed, delivered_at=delivered
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} demo orders."))
        # Print the resulting breakdown.
        self.stdout.write("Status breakdown:")
        for value, label in Order.Status.choices:
            n = Order.objects.filter(status=value).count()
            if n:
                self.stdout.write(f"  {label}: {n}")

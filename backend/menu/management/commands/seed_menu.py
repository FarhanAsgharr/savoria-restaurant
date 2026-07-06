"""
Seed the database with realistic demo categories and menu items.

Usage:
    python manage.py seed_menu           # add data (idempotent)
    python manage.py seed_menu --flush   # wipe menu data first, then seed

Each dish gets a generated warm-gradient placeholder image (via Pillow),
so the storefront looks complete without bundling real photography.
"""

from __future__ import annotations

import hashlib
import io
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image

from menu.models import Category, MenuItem

# ── Demo data ────────────────────────────────────────────────
CATEGORIES: list[dict] = [
    {
        "name": "Starters",
        "order": 1,
        "description": "Elegant small plates to awaken the palate.",
    },
    {
        "name": "Main Courses",
        "order": 2,
        "description": "Chef-crafted signature entrées.",
    },
    {
        "name": "Desserts",
        "order": 3,
        "description": "Sweet finales, made in-house daily.",
    },
    {
        "name": "Drinks",
        "order": 4,
        "description": "Curated wines, cocktails and soft beverages.",
    },
]

ITEMS: list[dict] = [
    # (category, name, price, featured, description)
    ("Starters", "Seared Scallops", "16.50", True,
     "Pan-seared sea scallops on a cauliflower purée with brown-butter vinaigrette."),
    ("Starters", "Burrata & Heirloom Tomato", "13.00", False,
     "Creamy burrata, heirloom tomatoes, basil oil and aged balsamic."),
    ("Starters", "Wild Mushroom Arancini", "11.50", False,
     "Crispy risotto spheres with truffle aioli and parmesan."),
    ("Main Courses", "Filet Mignon", "38.00", True,
     "8oz grass-fed beef tenderloin, potato fondant and red-wine jus."),
    ("Main Courses", "Pan-Roasted Salmon", "27.00", True,
     "Atlantic salmon, lemon beurre blanc, seasonal greens."),
    ("Main Courses", "Wild Mushroom Risotto", "22.00", False,
     "Carnaroli rice, wild mushrooms, aged parmesan and white truffle oil."),
    ("Main Courses", "Herb-Crusted Lamb Rack", "34.00", False,
     "New Zealand lamb, rosemary crust, minted pea purée."),
    ("Desserts", "Molten Chocolate Cake", "10.50", True,
     "Warm dark-chocolate fondant with vanilla-bean ice cream."),
    ("Desserts", "Crème Brûlée", "9.00", False,
     "Classic vanilla custard with a caramelized sugar crust."),
    ("Desserts", "Lemon Tart", "8.50", False,
     "Zesty lemon curd in a buttery shortcrust with torched meringue."),
    ("Drinks", "Signature Old Fashioned", "14.00", False,
     "Bourbon, bitters, demerara and orange zest."),
    ("Drinks", "Barolo (Glass)", "16.00", False,
     "Full-bodied Italian red with notes of cherry and spice."),
    ("Drinks", "Fresh Citrus Cooler", "6.50", False,
     "House lemonade with mint and sparkling water."),
]


def _gradient_image(seed: str, size: tuple[int, int] = (800, 600)) -> ContentFile:
    """Create a deterministic warm diagonal-gradient JPEG for a given seed."""
    digest = hashlib.md5(seed.encode()).hexdigest()
    # Two warm anchor colors derived from the hash.
    top = (
        150 + int(digest[0:2], 16) % 90,
        90 + int(digest[2:4], 16) % 80,
        50 + int(digest[4:6], 16) % 60,
    )
    bottom = (
        40 + int(digest[6:8], 16) % 40,
        25 + int(digest[8:10], 16) % 30,
        20 + int(digest[10:12], 16) % 25,
    )
    width, height = size
    base = Image.new("RGB", size)
    px = base.load()
    for y in range(height):
        t = y / height
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(width):
            px[x, y] = (r, g, b)
    buffer = io.BytesIO()
    base.save(buffer, format="JPEG", quality=82)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "Seed the database with demo categories and menu items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing categories and menu items before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            MenuItem.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing menu data flushed."))

        categories: dict[str, Category] = {}
        for data in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "display_order": data["order"],
                },
            )
            categories[data["name"]] = category

        created = 0
        for cat_name, name, price, featured, description in ITEMS:
            if MenuItem.objects.filter(name=name).exists():
                continue
            item = MenuItem(
                category=categories[cat_name],
                name=name,
                description=description,
                price=Decimal(price),
                is_featured=featured,
                is_available=True,
            )
            item.image.save(
                f"{item.name.lower().replace(' ', '-')}.jpg",
                _gradient_image(name),
                save=False,
            )
            item.save()
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {len(categories)} categories, {created} new items."
            )
        )

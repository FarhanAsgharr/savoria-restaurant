"""
Seed the database with realistic demo categories and menu items.

Usage:
    python manage.py seed_menu           # add/refresh data (idempotent)
    python manage.py seed_menu --flush   # wipe menu data first, then seed

Each dish gets an AI-generated photo (Pollinations text-to-image) matching its
exact description, downloaded and stored locally. Generation runs in parallel
for speed; if any image fails, it falls back to a warm-gradient placeholder so
images never end up broken.
"""

from __future__ import annotations

import hashlib
import io
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image

from menu.models import Category, MenuItem

# Generated photos are cached here so re-runs keep successes and only retry
# the dishes that failed (the free AI service rate-limits batches).
CACHE_DIR = Path(settings.BASE_DIR) / "seed_cache"
REAL_MIN_BYTES = 45000  # smaller than this ⇒ treat as a failed/placeholder image


def _cache_path(name: str) -> Path:
    return CACHE_DIR / (hashlib.md5(name.encode()).hexdigest() + ".jpg")


def _cached_photo(name: str) -> bytes | None:
    p = _cache_path(name)
    if p.exists() and p.stat().st_size > REAL_MIN_BYTES:
        return p.read_bytes()
    return None

# ── Demo data ────────────────────────────────────────────────
CATEGORIES: list[dict] = [
    {"name": "Starters", "order": 1, "description": "Elegant small plates to awaken the palate."},
    {"name": "Main Courses", "order": 2, "description": "Chef-crafted signature entrées."},
    {"name": "Desserts", "order": 3, "description": "Sweet finales, made in-house daily."},
    {"name": "Drinks", "order": 4, "description": "Curated wines, cocktails and soft beverages."},
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

# AI image prompts — a precise visual description of each dish.
PROMPTS: dict[str, str] = {
    "Seared Scallops": "pan-seared sea scallops on cauliflower puree with brown butter, elegant fine dining appetizer plated on white plate",
    "Burrata & Heirloom Tomato": "fresh burrata cheese with colorful heirloom tomatoes, basil oil and balsamic, fine dining appetizer",
    "Wild Mushroom Arancini": "crispy golden fried arancini risotto balls with truffle aioli and parmesan, fine dining appetizer",
    "Filet Mignon": "filet mignon beef tenderloin steak with potato fondant and red wine jus, fine dining plated main course",
    "Pan-Roasted Salmon": "pan-roasted salmon fillet with lemon butter sauce and seasonal green vegetables, fine dining plated",
    "Wild Mushroom Risotto": "creamy wild mushroom risotto with parmesan and truffle oil in a bowl, fine dining",
    "Herb-Crusted Lamb Rack": "herb-crusted rack of lamb chops with rosemary and pea puree, fine dining plated main course",
    "Molten Chocolate Cake": "molten chocolate lava cake with a scoop of vanilla ice cream, elegant dessert",
    "Crème Brûlée": "classic creme brulee with a caramelized golden sugar crust in a ramekin, dessert",
    "Lemon Tart": "lemon tart slice with torched meringue on top, elegant plated dessert",
    "Signature Old Fashioned": "old fashioned whiskey cocktail with a large ice cube and orange peel in a rocks glass, moody bar",
    "Barolo (Glass)": "a glass of deep red Barolo wine on a table in an elegant restaurant",
    "Fresh Citrus Cooler": "fresh sparkling lemonade citrus cooler with mint leaves and ice in a tall glass",
}

STYLE = "professional food photography, appetizing, natural soft light, shallow depth of field, high detail, no text, no watermark"

# Representative dish whose photo becomes each category's cover image.
CATEGORY_COVERS: dict[str, str] = {
    "Starters": "Seared Scallops",
    "Main Courses": "Filet Mignon",
    "Desserts": "Molten Chocolate Cake",
    "Drinks": "Signature Old Fashioned",
}


def _gradient_image(seed: str, size: tuple[int, int] = (1200, 900)) -> ContentFile:
    """Deterministic warm-gradient JPEG — the fallback when generation fails."""
    digest = hashlib.md5(seed.encode()).hexdigest()
    top = (150 + int(digest[0:2], 16) % 90, 90 + int(digest[2:4], 16) % 80, 50 + int(digest[4:6], 16) % 60)
    bottom = (40 + int(digest[6:8], 16) % 40, 25 + int(digest[8:10], 16) % 30, 20 + int(digest[10:12], 16) % 25)
    width, height = size
    base = Image.new("RGB", size)
    px = base.load()
    for y in range(height):
        t = y / height
        row = (
            int(top[0] * (1 - t) + bottom[0] * t),
            int(top[1] * (1 - t) + bottom[1] * t),
            int(top[2] * (1 - t) + bottom[2] * t),
        )
        for x in range(width):
            px[x, y] = row
    buffer = io.BytesIO()
    base.save(buffer, format="JPEG", quality=82)
    return ContentFile(buffer.getvalue())


def _generate(name: str) -> bytes | None:
    """Generate a dish photo via Pollinations AI (with retries). JPEG bytes or None."""
    prompt = f"{PROMPTS.get(name, name)}, {STYLE}"
    seed = int(hashlib.md5(name.encode()).hexdigest()[:6], 16)
    url = (
        "https://image.pollinations.ai/prompt/"
        + urllib.parse.quote(prompt)
        + f"?width=1024&height=768&nologo=true&seed={seed}"
    )
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                if resp.status == 200:
                    data = resp.read()
                    # Sanity check: a real photo, not an error page.
                    if data and len(data) > 5000:
                        return data
        except Exception:  # noqa: BLE001
            pass
        time.sleep(3 + attempt * 4)  # back off; the free service rate-limits
    return None


class Command(BaseCommand):
    help = "Seed demo categories and menu items with AI-generated dish photos."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true",
                            help="Delete existing categories and menu items first.")

    def handle(self, *args, **options):
        CACHE_DIR.mkdir(exist_ok=True)
        names = [row[1] for row in ITEMS]

        # 1) Only (re)generate dishes that aren't already cached as real photos.
        missing = [n for n in names if _cached_photo(n) is None]
        self.stdout.write(
            f"{len(names) - len(missing)}/{len(names)} already have AI photos; "
            f"generating {len(missing)}…"
        )

        def gen_and_cache(name: str):
            data = _generate(name)
            if data:
                _cache_path(name).write_bytes(data)
            return name, bool(data)

        if missing:
            with ThreadPoolExecutor(max_workers=3) as pool:
                for name, ok in pool.map(gen_and_cache, missing):
                    self.stdout.write(f"  • {name}: {'AI photo ✓' if ok else 'failed (retry next run)'}")

        # 2) Persist to the database (cached photo, or gradient fallback).
        with transaction.atomic():
            if options["flush"]:
                MenuItem.objects.all().delete()
                Category.objects.all().delete()
                self.stdout.write(self.style.WARNING("Existing menu data flushed."))

            categories: dict[str, Category] = {}
            for data in CATEGORIES:
                category, _ = Category.objects.get_or_create(
                    name=data["name"],
                    defaults={"description": data["description"], "display_order": data["order"]},
                )
                categories[data["name"]] = category

            for cat_name, name, price, featured, description in ITEMS:
                item, _ = MenuItem.objects.get_or_create(
                    name=name,
                    defaults={
                        "category": categories[cat_name],
                        "description": description,
                        "price": Decimal(price),
                        "is_featured": featured,
                        "is_available": True,
                    },
                )
                raw = _cached_photo(name)
                image = ContentFile(raw) if raw else _gradient_image(name)
                if item.image:
                    item.image.delete(save=False)
                item.image.save(f"{item.slug or item.pk}.jpg", image, save=True)

            # Give each category a cover image (reuse a representative dish photo).
            for cat_name, category in categories.items():
                rep_name = CATEGORY_COVERS.get(cat_name)
                rep = (
                    MenuItem.objects.filter(name=rep_name).first()
                    if rep_name
                    else category.items.first()
                )
                if rep and rep.image:
                    with rep.image.open("rb") as fh:
                        data = fh.read()
                    if category.image:
                        category.image.delete(save=False)
                    category.image.save(f"cat-{category.slug}.jpg", ContentFile(data), save=True)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {len(categories)} categories, {len(ITEMS)} items with images."
        ))

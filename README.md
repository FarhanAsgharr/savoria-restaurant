# 🍽️ Savoria — Restaurant Menu & Ordering Dashboard

A production-quality, full-stack restaurant menu and ordering platform: a
luxury storefront where guests browse a chef-curated menu, add dishes to a
cart, and place orders — backed by a Django REST API and a professional admin.

- **Backend:** Python 3.12 · Django 5 · Django REST Framework · PostgreSQL (SQLite in dev)
- **Frontend:** Next.js 15 (App Router) · React 18 · TypeScript · Tailwind CSS 3

<br />

## ✨ Features

**Storefront**
- Luxury, responsive design (mobile / tablet / desktop) with smooth animations
- Home page: hero, featured dishes, category tiles, "Our Story"
- Full menu with **live search**, **category filters**, and **sorting** (price / name)
- Category and dish detail pages with related dishes
- **Cart** with quantity steppers, `localStorage` persistence, and cross-tab sync
- **Checkout** with an accessible, validated form → real order submission
- **Order confirmation** page with itemised summary and status
- Skeleton loading states, empty states, error boundaries, and a custom 404
- SEO metadata, `next/image` optimization, keyboard-accessible navigation

**Backend**
- Four models: `Category`, `MenuItem`, `Order`, `OrderItem`
- Professional Django Admin (thumbnails, inline order items, filters, search)
- REST API via DRF `ModelViewSet`s with pagination, search, filtering, ordering
- **Server-side price snapshots & totals** — clients can't tamper with prices
- 12-factor configuration, secure CORS, structured logging, production hardening
- 24 automated tests (models + API)

<br />

## 🗂️ Project structure

```
restaurant-app/
├── README.md
├── DEPLOYMENT.md              # Render + Vercel deployment guide
│
├── backend/                   # Django 5 + DRF
│   ├── config/                # project package (settings, urls, wsgi/asgi)
│   ├── menu/                  # the app
│   │   ├── models.py          # Category, MenuItem, Order, OrderItem
│   │   ├── admin.py           # professional admin
│   │   ├── serializers.py     # read/write serializers + validation
│   │   ├── views.py           # ViewSets
│   │   ├── filters.py         # category / price / availability filters
│   │   ├── urls.py            # DRF router
│   │   ├── management/commands/seed_menu.py
│   │   └── tests/             # test_models.py, test_api.py
│   ├── requirements.txt
│   ├── Procfile / render.yaml / build.sh / runtime.txt
│   └── .env.example
│
└── frontend/                  # Next.js 15 (App Router)
    └── src/
        ├── app/               # routes: /, /menu, /menu/[category]/[item],
        │                      #         /cart, /checkout, /order/[id], 404, error
        ├── components/        # Navbar, Footer, FoodCard, CartButton, …
        ├── context/           # CartContext (localStorage-backed)
        ├── lib/               # api client, formatters
        └── types/             # shared TypeScript types
```

<br />

## 🚀 Local development

### Prerequisites
- Python **3.12+**
- Node.js **20+**
- (Optional) PostgreSQL 14+ — SQLite is used by default in dev

### 1 · Backend

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate                 # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                      # edit as needed
python manage.py migrate
python manage.py seed_menu                # demo categories + dishes (with images)
python manage.py createsuperuser          # for the admin
python manage.py runserver                # http://127.0.0.1:8000
```

- API root → `http://127.0.0.1:8000/api/`
- Admin → `http://127.0.0.1:8000/admin/`
- Health → `http://127.0.0.1:8000/healthz/`

### 2 · Frontend

```bash
cd frontend
npm install
cp .env.example .env.local                # points NEXT_PUBLIC_API_URL at the backend
npm run dev                               # http://localhost:3000
```

<br />

## 🔌 API reference

Base URL: `/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/categories/` | List active categories (with available-item counts) |
| `GET`  | `/categories/{slug}/` | Category detail |
| `GET`  | `/items/` | List menu items (paginated) |
| `GET`  | `/items/{slug}/` | Menu item detail |
| `POST` | `/orders/` | Place an order |
| `GET`  | `/orders/{id}/` | Retrieve an order |

**Query params on `/items/`:**
`?category=<id|slug>` · `?is_available=true` · `?is_featured=true` ·
`?min_price=` · `?max_price=` · `?search=<term>` ·
`?ordering=price|-price|name` · `?page=<n>`

**Create-order payload:**
```json
{
  "customer_name": "Ada Lovelace",
  "customer_email": "ada@example.com",
  "customer_phone": "",
  "address": "",
  "notes": "",
  "items": [{ "menu_item": 4, "quantity": 2 }]
}
```
> Prices and the order total are computed **server-side** from the database —
> any price sent by the client is ignored.

<br />

## ✅ Testing

```bash
cd backend
python manage.py test                     # 24 tests: models + API

cd frontend
npm run type-check                         # tsc --noEmit
npm run lint                               # ESLint
npm run build                              # production build
```

<br />

## ♿ Accessibility

- Semantic landmarks (`header`, `nav`, `main`, `footer`) + a skip-to-content link
- Labelled form fields with `aria-invalid` / `aria-describedby` error wiring
- Visible focus rings, keyboard-operable menus, `aria-current` on active nav
- Descriptive `alt` text and accessible cart/quantity controls

<br />

## 🌐 Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** — backend to **Render** (blueprint
included) or Railway, frontend to **Vercel**. All secrets via environment
variables.

<br />

## 📦 Build phases

| Phase | Scope |
|-------|-------|
| **0** | Monorepo, tooling, base config |
| **1** | Models, admin, REST API, storefront (Home / Menu / Categories) |
| **2** | Cart, checkout, order confirmation |
| **3** | Search & sort polish, tests, accessibility, docs |

<br />

## 📄 License

MIT

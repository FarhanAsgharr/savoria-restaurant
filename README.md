# 🍽️ Savoria — Restaurant Menu & Ordering Dashboard

A production-quality, full-stack restaurant menu and ordering platform.

- **Backend:** Django 5 + Django REST Framework + PostgreSQL (SQLite for dev)
- **Frontend:** Next.js 15 (App Router) + React + TypeScript + Tailwind CSS

This is a monorepo:

```
restaurant-app/
├── backend/     # Django REST API + Admin
└── frontend/    # Next.js 15 storefront
```

---

## 🚀 Quick start

### Prerequisites

- Python **3.12+**
- Node.js **20+**
- (Optional) PostgreSQL 14+ — SQLite is used by default in development

### 1. Backend

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # then edit values as needed
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver          # http://127.0.0.1:8000
```

API root: `http://127.0.0.1:8000/api/`
Admin: `http://127.0.0.1:8000/admin/`

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local          # points at the backend API
npm run dev                         # http://localhost:3000
```

---

## 📦 Project phases

| Phase | Scope |
|-------|-------|
| **0** | Project setup, monorepo, tooling, base config |
| **1** | Models, Admin, REST API, Home / Menu / Categories, deploy |
| **2** | Orders, Cart, Checkout |
| **3** | Search, testing, accessibility, docs |

---

## 🌐 Deployment

- **Backend** → Render / Railway (Gunicorn + PostgreSQL)
- **Frontend** → Vercel

All secrets are supplied via environment variables. See `.env.example` in each package.

---

## 📄 License

MIT

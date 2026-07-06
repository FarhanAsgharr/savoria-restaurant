# 🚀 Deployment Guide

Deploy the **backend** to Render (or Railway) and the **frontend** to Vercel.

---

## Backend → Render

The repo ships a `backend/render.yaml` Blueprint that provisions the web
service **and** a PostgreSQL database in one step.

1. Push the repo to GitHub.
2. In Render → **New → Blueprint**, select the repo. Render reads
   `backend/render.yaml`.
3. After the first deploy, set these environment variables on the service
   (values marked `sync: false`):
   - `ALLOWED_HOSTS` → `savoria-api.onrender.com`
   - `CORS_ALLOWED_ORIGINS` → `https://<your-vercel-app>.vercel.app`
   - `CSRF_TRUSTED_ORIGINS` → `https://<your-vercel-app>.vercel.app`
4. `SECRET_KEY` is auto-generated, `DATABASE_URL` is wired from the DB, and
   `build.sh` runs `collectstatic` + `migrate` automatically.
5. Create an admin user via the Render **Shell**:
   ```bash
   python manage.py createsuperuser
   python manage.py seed_menu   # optional demo data
   ```

Health check: `GET /healthz/`

### Railway (alternative)
Railway auto-detects the `backend/Procfile`. Add a PostgreSQL plugin, then set
the same environment variables. The `release:` line runs migrations on deploy.

---

## Frontend → Vercel

1. In Vercel → **New Project**, import the repo and set the **Root Directory**
   to `frontend`.
2. Add environment variables:
   - `NEXT_PUBLIC_API_URL` → `https://savoria-api.onrender.com/api`
   - `NEXT_PUBLIC_IMAGE_HOST` → `savoria-api.onrender.com`
3. Deploy. Vercel auto-detects Next.js (build `next build`, output handled).

> `NEXT_PUBLIC_IMAGE_HOST` adds the backend host to the `next/image`
> optimization allow-list (see `frontend/next.config.ts`).

---

## Post-deploy checklist

- [ ] Backend `/healthz/` returns `{"status": "ok"}`
- [ ] `/api/categories/` returns data
- [ ] Frontend home page loads featured dishes & categories
- [ ] CORS: no console errors calling the API from the Vercel domain
- [ ] Admin login works at `/admin/`

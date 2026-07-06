# 🚀 Deployment Guide (Vercel + Render)

Get permanent, public links that work on **any** network:

- **Backend + Admin** → Render (free) + PostgreSQL
- **Customer website** → Vercel (free)

Total time: ~20–30 minutes. You need three free accounts:
[GitHub](https://github.com) · [Render](https://render.com) · [Vercel](https://vercel.com)
(Sign in to Render and Vercel *with your GitHub account* — it's the easiest.)

---

## Step 1 — Put the code on GitHub

**Option A — GitHub CLI (easiest):**
```bash
gh auth login          # choose GitHub.com → HTTPS → login in browser
cd /Users/muhammad/Desktop/Resturant
gh repo create savoria --public --source=. --remote=origin --push
```

**Option B — manually:**
1. Create a new **empty** repo at https://github.com/new named `savoria` (no README).
2. Then:
   ```bash
   cd /Users/muhammad/Desktop/Resturant
   git remote add origin https://github.com/<your-username>/savoria.git
   git push -u origin main
   ```

---

## Step 2 — Deploy the backend to Render

1. Go to **https://dashboard.render.com** → **New → Blueprint**.
2. Connect your GitHub and select the **savoria** repo. Render reads
   `backend/render.yaml` and sets up the web service **+ PostgreSQL** automatically.
3. It will ask you to fill the values marked "set in dashboard":
   - **`DJANGO_SUPERUSER_PASSWORD`** → choose an admin password (remember it!).
   - **`FRONTEND_URL`** → leave blank for now (you'll add the Vercel URL in Step 4).
4. Click **Apply**. Wait for the build (it installs deps, migrates, seeds the
   menu, and creates the `admin` user).
5. When live you'll get a URL like `https://savoria-api.onrender.com`. Check:
   - `https://savoria-api.onrender.com/healthz/` → `{"status":"ok"}`
   - `https://savoria-api.onrender.com/admin/` → login `admin` / *(your password)*
   - `https://savoria-api.onrender.com/api/categories/` → JSON data

> 📌 Copy the backend URL — you need it in Step 3.
> ⚠️ Render free tier sleeps after 15 min idle; the first request then takes
> ~30–60s to wake. Totally fine for a demo.

---

## Step 3 — Deploy the frontend to Vercel

1. Go to **https://vercel.com/new** → import the **savoria** repo.
2. Set **Root Directory** to `frontend`.
3. Add two **Environment Variables**:
   | Name | Value |
   |------|-------|
   | `BACKEND_ORIGIN` | `https://savoria-api.onrender.com` *(your Step 2 URL)* |
   | `NEXT_PUBLIC_IMAGE_HOST` | `savoria-api.onrender.com` *(no https://)* |
4. Click **Deploy**. You'll get a URL like `https://savoria.vercel.app`.

That's your **customer website link** — send this one to your teacher. 🎉

---

## Step 4 — Connect them (final touch)

1. In **Render** → your service → **Environment** → set
   `FRONTEND_URL` = `https://savoria.vercel.app` → save (redeploys).
   *(This makes the admin's "VIEW SITE" button open the real customer site.)*

Done. Test the whole flow:
- Open `https://savoria.vercel.app`, browse the menu, add to cart, checkout.
- The order appears in `https://savoria-api.onrender.com/admin/` → Orders.

---

## How it fits together

```
Customer ──► Vercel (Next.js)  ──►  /api proxy  ──►  Render (Django API) ──► PostgreSQL
Teacher  ──► Render /admin/ (Django Admin) ────────────────────────────────┘
```

The browser only ever talks to the Vercel site (same-origin `/api`), which
forwards to Render server-side — so there are no CORS issues and no backend
URL exposed to the browser.

---

## Notes

- **Images:** the demo dish images are generated during the Render build. On
  the free tier the disk resets on redeploy, but the build re-seeds them, so
  they're always present.
- **Custom domain:** both Vercel and Render let you add one later for free.
- **Security:** change the admin password from any default; don't commit real
  secrets (they're all environment variables).

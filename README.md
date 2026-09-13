# 🚗 Samko Cars — Full-Stack Automotive Marketplace

A production-ready, full-stack car sales and dealership platform built for the Nigerian automotive market. Inspired by modern automotive marketplaces, Samko Cars combines a high-performance customer-facing marketplace with an authenticated executive administrative dashboard.

Built strictly with **Python, Django 5, Django REST Framework, PostgreSQL, HTML5, Vanilla CSS3, and JavaScript**.

---

## 🌟 Key Features

### 🛒 Customer-Facing Marketplace
- **Hero & Live Search**: Filter by Make, Model, Maximum Price (₦), and Location directly from the homepage.
- **Dynamic Inventory (`/cars/`)**: Full faceted search, sorting (Newest, Oldest, Price Low→High, Price High→Low, Mileage), and filtering by condition (Foreign Used / Tokunbo, Nigerian Used, Brand New), transmission, fuel type, body type, and price range.
- **Vehicle Details (`/cars/<id>/` & `/cars/<slug>/`)**: High-resolution gallery with thumbnail switcher, full specs grid, dynamic feature tags, WhatsApp lead generator with auto-populated message, interactive enquiry modal, and purchase/inspection request modal.
- **WhatsApp Integration**: Direct click-to-chat buttons dynamically configured with vehicle details and dealership phone line.
- **Responsive Mobile-First UX**: Fully responsive layouts tested for desktop, laptop, tablet, mobile phones (320px+), and smartwatch/wearables with an accessible off-canvas hamburger navigation.
- **Dark & Light Mode**: Seamless theme switcher with persistent user preference saved via `localStorage`.
- **Nigerian Naira (₦)**: Clean formatting of decimal currency values with comma separators.
- **SEO Ready**: Dynamic meta tags, Open Graph card tags, semantic HTML5, `robots.txt`, and XML sitemap (`/sitemap.xml`).

### 🛡️ Private Admin Dashboard (`/admin-panel/`)
- **Protected Access**: Django staff/superuser authentication with session management. Public users cannot access dashboard or administrative APIs.
- **Dashboard Overview**: Metrics for total cars, available, sold, reserved, featured, new enquiries, and purchase requests.
- **Complete Vehicle CRUD**: Add, edit, preview, and permanently delete vehicles with safety confirmation modal.
- **Live Inventory Toggles**: 1-click status switching between `AVAILABLE`, `RESERVED`, and `SOLD` (with sold badge display).
- **Homepage Feature Toggle**: 1-click feature/unfeature toggle for homepage showcase.
- **Multi-Image Management**: Multi-image file uploads, cover photo selection, and image deletion.
- **Enquiry Management (`/admin-panel/enquiries/`)**: Track customer enquiries, view contact details, click-to-WhatsApp, and update workflow status (`New`, `Contacted`, `Resolved`).
- **Purchase / Reservation Requests (`/admin-panel/purchases/`)**: Manage vehicle purchase orders and inspection bookings, price snapshotting at time of request, customer WhatsApp redirection, and statuses (`New`, `Contacted`, `Processing`, `Completed`, `Cancelled`).
- **Dealership CMS & Homepage Management (`/admin-panel/settings/`)**: Edit dealership name, logo, phone, WhatsApp number, email, address, opening hours, homepage hero headline/copy, about us company story, mission, vision, and footer text without writing code.
- **Social Media Management (`/admin-panel/social/`)**: Dynamically add, toggle, or delete social platforms (Instagram, Facebook, X, TikTok, YouTube, LinkedIn).
- **Testimonial Management (`/admin-panel/testimonials/`)**: Add and manage customer reviews.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13, Django 5.x |
| **API** | Django REST Framework |
| **Database** | PostgreSQL (Production) / SQLite (Local Dev fallback) |
| **Styling** | Vanilla CSS3 (Custom design system, CSS variables, dark/light mode) |
| **Frontend** | Vanilla JavaScript (ES6+, Fetch API, modals, toast alerts) |
| **Static Files** | WhiteNoise (Compressed Manifest Static Storage) |
| **WSGI Server** | Gunicorn |
| **Deployment** | Render (`render.yaml`, `build.sh`, `Procfile`) |

---

## 🛠️ Step-by-Step Render Deployment Guide

Follow these 10 steps to deploy the project to Render:

### Step 1: Create GitHub Repository
Create a new GitHub repository named `samko-cars` (private or public).

### Step 2: Push Project to GitHub
Initialize git, commit the codebase, and push to GitHub:
```bash
git init
git add .
git commit -m "Initial commit: Samko Cars full-stack dealership"
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/samko-cars.git
git push -u origin main
```

### Step 3: Create PostgreSQL Database on Render
1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **PostgreSQL**.
3. Set the name to `samko-cars-db` and database name to `samko_db`.
4. Click **Create Database**.
5. Once provisioned, copy the **Internal Database URL** (e.g. `postgresql://samko_user:...@dpg-...-a/samko_db`).

### Step 4: Create Django Web Service
1. In Render Dashboard, click **New +** → **Web Service**.
2. Select **Build and deploy from a Git repository** and connect your `samko-cars` repo.
3. Choose the **Python** environment.

### Step 5: Connect Repository & Configure Build/Start Commands
- **Name**: `samko-cars`
- **Region**: Oregon (or nearest to your database)
- **Branch**: `main`
- **Build Command**: `bash build.sh`
- **Start Command**: `gunicorn config.wsgi:application`

*(Alternatively, if you use Blueprint deployment, Render will automatically detect `render.yaml` and configure both web service and database together).*

### Step 6: Add Environment Variables
In the **Environment** tab of your Web Service, add:
- `PYTHON_VERSION` = `3.13.2`
- `SECRET_KEY` = *(generate a secure 50+ character string or click generate)*
- `DEBUG` = `False`
- `ALLOWED_HOSTS` = `.onrender.com`
- `DATABASE_URL` = *(Paste the Internal Database URL from Step 3)*
- `CSRF_TRUSTED_ORIGINS` = `https://<YOUR-RENDER-SERVICE-NAME>.onrender.com`
- `EMAIL_BACKEND` = `django.core.mail.backends.console.EmailBackend` *(or SMTP credentials)*

### Step 7: Automated Migrations & Static Collection
When Render builds your app, `build.sh` automatically:
1. Installs all packages in `requirements.txt`
2. Runs `python manage.py collectstatic --no-input`
3. Applies database migrations with `python manage.py migrate --no-input`
4. Automatically populates initial site settings and demo vehicles if database is empty via `python manage.py seed_cars --quiet`

The bundled demo vehicle images are committed under `media/`. Admin uploads use local `FileSystemStorage` during development. Production uploads require an S3-compatible bucket because Render's web-service filesystem is ephemeral. Set `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_S3_REGION_NAME`; set `AWS_S3_ENDPOINT_URL` for providers such as Cloudflare R2 or Backblaze B2, and optionally set `AWS_S3_CUSTOM_DOMAIN`. The application switches to `django-storages` automatically when `AWS_STORAGE_BUCKET_NAME` is present. `AWS_LOCATION` defaults to `media`.

### Step 8: Create Administrator Account
In your Render Dashboard:
1. Open your Web Service.
2. Go to the **Shell** tab on the left menu.
3. Run:
```bash
python manage.py createsuperuser
```
4. Enter your username, email, and password.

### Step 9: Verify Static Files
WhiteNoise serves all static assets directly through Gunicorn with gzip compression and immutable caching headers.

### Step 10: Open the Website
Open your live URL: `https://<YOUR-APP-NAME>.onrender.com`.
- Visit the public homepage: `https://<YOUR-APP-NAME>.onrender.com/`
- Visit the administrative dashboard: `https://<YOUR-APP-NAME>.onrender.com/admin-panel/`

---

## 💻 Local Development Setup

### 1. Clone & Setup Virtual Environment
```bash
git clone <repo-url> samko-cars
cd samko-cars
python -m venv venv

# Windows:
.\venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Run Migrations & Seed Inventory
```bash
python manage.py migrate
python manage.py seed_cars
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Test Suite
```bash
python manage.py test apps.cars --keepdb
```

### 7. Start Development Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/`.

---

## 📡 REST API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/cars/api/v1/cars/` | List all active vehicles with pagination & search | Public |
| `GET` | `/cars/api/v1/cars/<id>/` | Detailed specs, features, and images of a car | Public |
| `POST` | `/cars/api/v1/cars/` | Add new vehicle | Admin only |
| `PUT` | `/cars/api/v1/cars/<id>/` | Full update of vehicle | Admin only |
| `DELETE` | `/cars/api/v1/cars/<id>/` | Delete vehicle | Admin only |

---

## 🔒 Security Best Practices Implemented
- **CSRF Protection**: All POST/AJAX forms include Django CSRF tokens.
- **Authentication & Authorization**: Strict `@staff_required` decorators on all `/admin-panel/` routes.
- **SQL Injection Prevention**: 100% parameterised queries through Django ORM.
- **XSS & Clickjacking Protection**: Secure headers and Django template escaping enabled.
- **Production SSL / HSTS**: Automated HTTPS redirection and secure cookie flags when `DEBUG=False`.
- **Secret Isolation**: `SECRET_KEY`, database credentials, and API keys managed strictly through environment variables.

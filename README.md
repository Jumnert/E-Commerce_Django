# E-Commerce Django — SkincareShop

A Django-based e-commerce storefront built with Bootstrap and common JS plugins (Owl Carousel, Lightbox). This project includes a `store` app (products, cart, checkout), templates, static assets, and a small admin setup. It is ready for local development and deployment (Gunicorn + Whitenoise).

---

## Requirements

## Local development setup (Windows)

1. Create and activate a virtual environment:

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```cmd
pip install -r requirements.txt
```

3. Apply database migrations:

```cmd
python manage.py migrate
```

4. (Optional) Create an admin user:

```cmd
python manage.py createsuperuser
```

5. Run the development server:

```cmd
python manage.py runserver
```

6. Open `http://127.0.0.1:8000/` in your browser.

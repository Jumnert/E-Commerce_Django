# E-Commerce Django — SkincareShop

A Django-based e-commerce storefront built with Bootstrap and common JS plugins (Owl Carousel, Lightbox). This project includes a `store` app (products, cart, checkout), templates, static assets, and a small admin setup. It is ready for local development and deployment (Gunicorn + Whitenoise).

---

## Quick links

- Project root: `manage.py`
- Main app: `store/`
- Templates: `templates/`
- Static assets: `jewelryshop/static/`
- Settings: `jewelryshop/settings.py`

## Features

- Product listing, category pages, product detail
- Shopping cart, checkout and order receipt pages
- Admin interface supported (Django admin + UI packages included)
- Static assets include Bootstrap, Owl Carousel, Lightbox, and custom theme files
- Dark theme (site-wide) and Bootstrap dark overrides included

## What I changed (theme)

- Added a site-wide dark theme file: `jewelryshop/static/css/style.dark.css`.
- Added Bootstrap overrides for dark mode: `jewelryshop/static/vendor/bootstrap/css/bootstrap-dark.css`.
- Updated `templates/base.html` to load the dark theme by default (the file references `css/style.dark.css` and the Bootstrap dark override).

If you'd like to revert to the original light theme, edit `templates/base.html` and set the `theme-stylesheet` link back to `css/style.default.css`, and remove or comment the Bootstrap dark override include.

## Requirements

This project uses Python and Django. See `requirements.txt` for exact package versions. Key packages include:

- `Django==6.0`
- `gunicorn`
- `whitenoise`
- `pillow`

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

Notes:

- The repository includes `db.sqlite3` for development. For production use a managed DB (Postgres, etc.) and update `jewelryshop/settings.py` accordingly.

## Static files & media

- Static files live in `jewelryshop/static/`.
- Uploaded media go to the `media/` folder (product images, payment proofs).
- For production, collect static files before starting the app:

```cmd
python manage.py collectstatic --noinput
```

Whitenoise is included in `requirements.txt` and can serve static files when using Gunicorn.

## Environment variables / production configuration

Set the following (at minimum) in your production environment:

- `DJANGO_SECRET_KEY` or replace `SECRET_KEY` in `jewelryshop/settings.py` securely
- `DEBUG=False`
- `ALLOWED_HOSTS` (comma-separated or list)
- Database credentials (if not using SQLite)

Example `.env` (do NOT commit this file):

```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@host:port/dbname
```

## Deployment notes

This project includes a `Procfile` and `runtime.txt` which make it compatible with Heroku-style deploys. Typical deployment steps:

1. Set environment variables on host (SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, DB credentials).
2. Install dependencies and run migrations.
3. Run `collectstatic`.
4. Start Gunicorn using the project's WSGI module (example Procfile):

```procfile
web: gunicorn jewelryshop.wsgi --log-file -
```

Whitenoise can serve static files directly when using Gunicorn.

## Tests

No automated tests are included by default. Run Django tests with:

```cmd
python manage.py test
```

## Suggestions & next steps you might want

- Add a JS-based theme toggle (store the user's preference in `localStorage` or a cookie) so users can switch light/dark at runtime.
- Create dark variants for the other theme files (e.g., `style.blue.dark.css`) if you want multiple color themes in dark mode.
- Minify `style.dark.css` and `bootstrap-dark.css` for production to reduce payload size.
- Move CSS to SCSS with variables for easier theming.

## Contributing

If you'd like help implementing features or improving the theme/toggle, open an issue or send a pull request. Small helpful tasks:

- Add a theme switch and persist user preference.
- Optimize and minify CSS assets for production.
- Add unit tests for critical parts of the `store` app.

## License

See the `LICENSE` file at the repository root for license information.

---

If you want, I can now:

- add a theme toggle UI and persist selection, or
- minify the dark CSS files and add `.min.css` versions, or
- generate dark variants for all available theme files.

Tell me which next step you want and I'll implement it.

# Scrap Recycling Backend (Flask + MySQL)

A beginner-friendly backend API for a scrap recycling platform with two roles: **collector** and **recycler**.

## 1. Features

- Session-based registration, login, logout and current-user endpoint.
- Collector listing create/read/update/delete operations.
- Recycler scrap-rate create/read/update/delete operations.
- Recycler-to-collector requests and collector decisions.
- Role-based dashboard and profile APIs.
- 19 fixed scrap categories.
- Optional listing image uploads (PNG/JPG/JPEG/WEBP, max size configured in `.env`).
- Password hashing using Werkzeug. Password hashes are never returned by the API.

## 2. Requirements

- Python 3.10 or newer
- MySQL Server
- Postman (for API testing)

## 3. MySQL setup

Open MySQL Workbench or the MySQL command line and run:

```sql
CREATE DATABASE scrap_recycling
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Create a MySQL user if you do not want to use `root`:

```sql
CREATE USER 'scrap_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON scrap_recycling.* TO 'scrap_user'@'localhost';
FLUSH PRIVILEGES;
```

Update `DATABASE_URL` in `.env`:

```text
mysql+pymysql://scrap_user:StrongPassword123!@localhost/scrap_recycling
```

If your password contains characters such as `@`, `#`, `/` or `:`, URL-encode those characters in the connection string.

## 4. Install and run

From this `Backend` directory:

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`, then create tables once:

```powershell
flask --app app shell
```

At the Python prompt:

```python
from extensions import db
db.create_all()
exit()
```

Run the server:

```powershell
py app.py
```

The API runs at `http://127.0.0.1:5000`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app shell
```

Then run `db.create_all()` in the shell, exit, and start with `python app.py`.

> `db.create_all()` creates missing tables. For a production project, use Flask-Migrate/Alembic for schema changes rather than relying on `create_all()`.

## 5. Session authentication in Postman

Login creates a Flask session cookie. Postman normally stores and resends cookies for the same host automatically. Use the same base URL for all requests (`127.0.0.1`, not a mix of `localhost` and `127.0.0.1`). Do not manually send a user ID to authenticate.

Register one collector and one recycler, then log in as the role needed for each endpoint.

## 6. API response format

Success:

```json
{
  "success": true,
  "message": "Listing created",
  "data": {}
}
```

Error:

```json
{
  "success": false,
  "message": "Login required"
}
```

Common HTTP codes: `200` success, `201` created, `400` invalid input, `401` not logged in/invalid credentials, `403` wrong role or ownership, `404` record not found, `409` duplicate/conflicting state, `413` upload too large.

## 7. Endpoint reference

All request bodies are JSON unless noted. For listing create/update with an image, use `multipart/form-data` with the text fields below and an `image` file field.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Register collector/recycler |
| POST | `/api/auth/login` | Public | Start session |
| POST | `/api/auth/logout` | Logged in | End session |
| GET | `/api/auth/me` | Logged in | Current user |
| GET | `/api/categories` | Public | Return all 19 categories |
| POST | `/api/listings` | Collector | Create listing |
| GET | `/api/listings` | Public | Browse available listings; optional `?category=...` |
| GET | `/api/listings/my` | Collector | Own listings |
| GET | `/api/listings/{id}` | Logged in | Listing details |
| PATCH | `/api/listings/{id}` | Owning collector | Edit listing |
| DELETE | `/api/listings/{id}` | Owning collector | Delete listing |
| POST | `/api/requests` | Recycler | Send request |
| GET | `/api/requests/received` | Collector | Requests for own listings |
| GET | `/api/requests/sent` | Recycler | Requests sent by current recycler |
| PATCH | `/api/requests/{id}` | Related collector/recycler | Accept/reject/complete |
| GET | `/api/rates` | Public | Browse recycler rates; optional category |
| POST | `/api/rates` | Recycler | Add rate |
| PATCH | `/api/rates/{id}` | Owning recycler | Edit rate |
| DELETE | `/api/rates/{id}` | Owning recycler | Delete rate |
| GET | `/api/dashboard` | Logged in | Role-specific counts |
| GET | `/api/profile` | Logged in | View profile |
| PATCH | `/api/profile` | Logged in | Update profile |

### Example request bodies

**Register** `POST /api/auth/register`

```json
{
  "full_name": "Asha Sharma",
  "email": "asha@example.com",
  "phone": "9876543210",
  "password": "StrongPass123",
  "role": "collector",
  "location": "Ghaziabad"
}
```

**Login** `POST /api/auth/login`

```json
{"email": "asha@example.com", "password": "StrongPass123"}
```

**Create listing** `POST /api/listings`

```json
{
  "category": "cardboard_boxes",
  "quantity_kg": 12.5,
  "description": "Clean and dry cardboard boxes",
  "pickup_area": "Indirapuram",
  "contact_method": "Phone"
}
```

**Create recycler rate** `POST /api/rates`

```json
{
  "category": "cardboard_boxes",
  "price_per_kg": 12,
  "minimum_quantity_kg": 5,
  "conditions": "Clean and dry material only"
}
```

**Send request** `POST /api/requests`

```json
{
  "listing_id": 1,
  "offered_price_per_kg": 13,
  "message": "I can collect this material tomorrow."
}
```

**Accept or reject** `PATCH /api/requests/1` (collector)

```json
{"status": "accepted"}
```

**Mark completed** `PATCH /api/requests/1` (the recycler who sent it)

```json
{"status": "completed"}
```

**Update profile** `PATCH /api/profile`

```json
{"full_name": "Asha S.", "phone": "9876543210", "location": "Ghaziabad"}
```

### Image upload

In Postman select **Body → form-data**. Add:
- `category` (Text), e.g. `cardboard_boxes`
- `quantity_kg` (Text), e.g. `12.5`
- `pickup_area` (Text)
- `contact_method` (Text)
- `description` (Text, optional)
- `image` (File, optional)

Images are stored in `uploads/`; the listing response includes `image_path` and `image_url`. The upload folder is served at `/uploads/<filename>`.

## 8. Database relationships

- One user with role `collector` can own many listings.
- One user with role `recycler` can own many recycler rates.
- One listing can receive many requests.
- One recycler can send many requests.
- Foreign keys connect listings → users, rates → users, requests → listings and users.

Tables are created from the SQLAlchemy models: `users`, `listings`, `recycler_rates`, and `requests`.

## 9. Important project notes

- Keep `.env` private. Commit `.env.example`, not `.env`.
- In production, use HTTPS, a strong secret key, secure cookies, CSRF protection for cookie-authenticated state-changing requests, rate limiting, and a proper migration workflow.
- This starter backend uses Flask's default session cookie. For browser-based deployment, add CSRF protection before production use.
- Image validation checks extension and upload size. For production, also inspect actual file content/MIME and consider randomized storage outside the public web root.
- Listing deletion cascades to its requests. A collector accepting one request closes the listing; other pending requests remain in their existing state. Add a business rule to reject/cancel those requests if your project requires it.
- The backend intentionally contains no AI image recognition, CNN, prediction, or frontend code.

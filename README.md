# Blog API

A modern, production-oriented REST API for a blog platform built with **FastAPI**. It provides full user authentication (JWT access + refresh tokens), CRUD operations for blog posts, image uploads to Cloudinary, rate limiting, and structured database migrations with Alembic.

---

## Overview

This project is a backend-only blog API. It lets users register and log in, and then create, read, update, publish, and delete blog posts — optionally attaching an image to each post (stored in Cloudinary).

The API is designed with:

- **JWT-based authentication** — short-lived access tokens plus long-lived refresh tokens.
- **Ownership-based authorization** — users can only update/publish posts they created.
- **Rate limiting** — protects auth and post-creation endpoints from abuse.
- **Type-safe request/response validation** — powered by Pydantic v2.
- **SQLAlchemy ORM + Alembic** — schema management for PostgreSQL.

---

## Features

### Authentication (JWT)
- User registration with email uniqueness checks (`POST /auth/register`)
- Login that verifies bcrypt-hashed passwords (`POST /auth/login`)
- Refresh token rotation to obtain new access tokens (`POST /auth/refresh`)
- Logout that invalidates the stored refresh token (`POST /auth/logout`)
- Current-user introspection (`GET /auth/me`)
- Fetch user details by ID (`GET /auth/get_user_by_id/{id}`)

### Posts
- List all posts (`GET /posts`)
- List unpublished posts (`GET /posts/unpublished`)
- Get a single post by ID (`GET /posts/{id}`)
- Create a post using multipart form data with an optional image (`POST /posts`)
- Partially update a post's title/content — owner only (`PUT /posts/{id}`)
- Toggle the published state — owner only (`PATCH /posts/{id}/published`)
- Delete a post (also removes its image from Cloudinary) (`DELETE /posts/{id}`)

### Security & Robustness
- Passwords hashed with **bcrypt** (salted)
- JWT tokens signed with **python-jose** (`HS256`)
- **slowapi** rate limits: `5/minute` on register/login, `10/hour` on post creation
- Automatic **Cloudinary** image upload/cleanup for post images
- Global exception handling for rate-limit violations

### Database
- PostgreSQL via **SQLAlchemy 2.0** (psycopg2 driver)
- Model relationships with cascade delete (deleting a user removes their posts)
- **Alembic** migration history under `alembic/versions/`
- Tables auto-created on startup (`Base.metadata.create_all`) in addition to migrations

---

## Tools & Technologies

| Category        | Technology                                            |
|-----------------|-------------------------------------------------------|
| Language        | Python 3.10+                                          |
| Web framework   | [FastAPI](https://fastapi.tiangolo.com/)              |
| ASGI server     | [Uvicorn](https://www.uvicorn.org/)                   |
| ORM             | SQLAlchemy 2.0                                        |
| Database        | PostgreSQL (via `psycopg2-binary`)                    |
| Migrations      | Alembic                                              |
| Validation      | Pydantic v2 + pydantic-settings                      |
| Auth            | python-jose (JWT), HTTPBearer, bcrypt                |
| Image storage   | Cloudinary SDK                                       |
| Rate limiting   | slowapi                                              |
| File uploads    | python-multipart                                     |
| Email parsing   | email-validator (`EmailStr`)                         |
| Env management  | python-dotenv / pydantic-settings                    |

---

## Project Structure

```
blog-api/
├── main.py                  # Entry point: runs uvicorn on app.main:app
├── requirements.txt         # Python dependencies
├── alembic.ini              # Alembic configuration
├── .env.example             # Sample environment variables
├── app/
│   ├── main.py              # FastAPI app instance, routes, exception handlers
│   ├── config.py            # App settings loaded from .env
│   ├── database.py          # Engine, session factory, get_db dependency
│   ├── models/
│   │   ├── user.py          # User SQLAlchemy model
│   │   └── post.py          # Post SQLAlchemy model
│   ├── schemas/
│   │   ├── user.py          # Pydantic models for users (create/login/response)
│   │   └── post.py          # Pydantic models for posts (create/update/response)
│   ├── routers/
│   │   ├── auth.py          # /auth endpoints
│   │   └── posts.py         # /posts endpoints
│   └── utils/
│       ├── jwt.py           # Access/refresh token creation & verification
│       ├── hashing.py       # bcrypt password hashing helpers
│       ├── dependencies.py  # get_current_user dependency (bearer auth)
│       ├── cloudinary.py    # Image upload/delete helper
│       └── limiter.py       # Shared slowapi limiter instance
└── alembic/
    └── versions/            # Migration scripts
```

---

## Getting Started

### Prerequisites

- **Python 3.10+** installed
- **PostgreSQL** running locally (or a hosted instance such as Neon, RDS, or Supabase)
- **Git** (only if you are cloning the repository)

### 1. Clone & enter the project

```bash
git clone <repo-url>
cd blog-api
```

### 2. Create and activate a virtual environment

```powershell
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# Windows (Cmd.exe)
python -m venv venv
.\venv\Scripts\activate.bat
```

```bash
# macOS / Linux / Git Bash / WSL
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and edit it:

```powershell
# PowerShell
Copy-Item .env.example .env
```

```bash
# Cmd.exe / bash
copy .env.example .env
```

Below is the full list of variables the application reads (see `app/config.py`):

| Variable                     | Required | Default                        | Description                                   |
|------------------------------|----------|--------------------------------|-----------------------------------------------|
| `DATABASE_URL`               | Yes      | —                              | PostgreSQL connection string                  |
| `SECRET_KEY`                 | Yes      | —                              | Secret used to sign/verify JWT tokens         |
| `ALGORITHM`                  | No       | `HS256`                        | JWT signing algorithm                         |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| No       | `15`                           | Access token lifetime (minutes)               |
| `REFRESH_TOKEN_EXPIRE_DAYS`  | No       | `7`                            | Refresh token lifetime (days)                 |
| `CLOUDINARY_CLOUD_NAME`      | If using images | —                      | Cloudinary cloud name                         |
| `CLOUDINARY_API_KEY`         | If using images | —                      | Cloudinary API key                            |
| `CLOUDINARY_API_SECRET`      | If using images | —                      | Cloudinary API secret                         |

> **Note:** the bundled `.env.example` only includes `DATABASE_URL` and `SECRET_KEY`. Add the three `CLOUDINARY_*` variables when you want to use post-image uploads.

Example `.env`:

```ini
DATABASE_URL=postgresql://username:password@localhost:5432/blog_db
SECRET_KEY=a-very-long-random-secret-string
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 5. Set up the database

You can either apply the Alembic migrations:

```bash
alembic upgrade head
```

or let the app create missing tables automatically on startup (it calls `Base.metadata.create_all` in `app/main.py`). Running migrations is the recommended approach.

### 6. Run the server

```bash
python main.py
```

or directly with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- **Base URL:** `http://localhost:8000`
- **Interactive docs (Swagger UI):** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## API Endpoints

### Health

| Method | Path   | Description          | Auth         |
|--------|--------|----------------------|--------------|
| `GET`  | `/`    | API health check     | Public       |

### Auth — prefix `/auth`

| Method | Path                     | Description                          | Auth        | Rate limit |
|--------|--------------------------|--------------------------------------|-------------|------------|
| `POST` | `/auth/register`         | Register a new user (returns tokens)| Public      | `5/minute` |
| `POST` | `/auth/login`            | Log in with email + password         | Public      | `5/minute` |
| `POST` | `/auth/refresh`          | Exchange refresh token for new access token | Public | —     |
| `POST` | `/auth/logout`           | Log out, invalidate stored refresh token | Bearer    | —     |
| `GET`  | `/auth/me`               | Get the authenticated user           | Bearer      | —          |
| `GET`  | `/auth/get_user_by_id/{id}` | Get a user by ID                  | Public      | —          |

### Posts — prefix `/posts` (all endpoints require a Bearer token)

| Method   | Path                       | Description                                   | Ownership check |
|----------|----------------------------|-----------------------------------------------|-----------------|
| `GET`    | `/posts/`                  | List all posts                                 | —               |
| `GET`    | `/posts/unpublished`       | List unpublished posts                         | —               |
| `GET`    | `/posts/{id}`              | Get a single post by ID                        | —               |
| `POST`   | `/posts/`                  | Create a post (multipart form, optional image) | —               |
| `PUT`    | `/posts/{id}`              | Update title/content of your post              | Yes             |
| `PATCH`  | `/posts/{id}/published`    | Publish / unpublish your post                  | Yes             |
| `DELETE` | `/posts/{id}`              | Delete your post (removes image too)           | —               |

> `POST /posts/` is rate-limited to `10/hour`.

### Auth flow (example)

1. `POST /auth/register` or `/auth/login` → receive `access_token` + `refresh_token`.
2. Call protected endpoints with the header:

   ```
   Authorization: Bearer <access_token>
   ```

3. When the access token expires (~15 min by default), call `POST /auth/refresh` with the refresh token body to get a new access token.

---

## Project credits / notes

- All schema and ORM definitions are Pydantic v2 (`model_config = {"from_attributes": True}`) and SQLAlchemy 2.0 typing style.
- The project was developed on **Python 3.14** locally, but works with Python 3.10+.
- Image uploads require a valid Cloudinary account and the corresponding credentials in `.env`.

---

## License

This project is for learning/demo purposes. Replace with your own license as needed.
# 💬 ReviewPulse: Backend API

FastAPI service behind [ReviewPulse](../README.md). It handles authentication, restaurant onboarding and data collection, the RAG-powered AI assistant, the guided question library, and Stripe subscription billing.

## 🛠️ Tech Stack

- **Framework:** FastAPI, Pydantic, Uvicorn
- **Database:** PostgreSQL, SQLAlchemy 2.0, Alembic migrations
- **AI:** OpenAI GPT-4o via LangChain, Pinecone, Sentence-Transformers embeddings
- **Integrations:** Stripe, SerpAPI (Google Maps), SMTP
- **Jobs:** APScheduler
- **Auth:** JWT (PyJWT), bcrypt (passlib)

## ⚙️ Setup

1. **Create and activate a virtual environment** (Python 3.11)
   ```bash
   cd BE
   python3.11 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Fill in the values. See [Environment variables](#-environment-variables) below.

3. **Create the database schema and seed the question library**
   ```bash
   alembic upgrade head
   python -m faq.seed
   ```

4. **Run the API**
   ```bash
   uvicorn app:app --reload
   ```
   The API runs at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

5. **Forward Stripe webhooks (local development)**
   ```bash
   stripe listen --forward-to localhost:8000/stripe/webhook
   ```
   Copy the printed signing secret into `STRIPE_WEBHOOK_SECRET`.

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `POSTGRES_CONNECTION_URI` | ✅ | e.g. `postgresql://user:pass@localhost:5432/reviewpulse` |
| `JWT_SECRET_KEY` | ✅ | Long random string used to sign tokens |
| `JWT_ALGORITHM` | | Default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | Default `1440` (24h) |
| `BASE_URL` | ✅ | Frontend URL, used in email links and as the allowed CORS / redirect origin |
| `CORS_ORIGINS` | | Extra allowed frontend origins, comma separated (e.g. `http://localhost:3000`) |
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `PINECONE_API_KEY` | ✅ | Pinecone API key |
| `PINECONE_INDEX` | ✅ | Pinecone index name (created automatically if missing, 384 dimensions) |
| `EMBEDDING_MODEL` | ✅ | e.g. `sentence-transformers/all-MiniLM-L6-v2` |
| `SERPAPI_API_KEY` | ✅ | SerpAPI key for Google Maps data |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | ✅ | Stripe webhook signing secret |
| `PRO_PRICE_ID` | ✅ | Stripe price ID for the Pro plan |
| `PREMIUM_PRICE_ID` | ✅ | Stripe price ID for the Premium plan |
| `SMTP_HOST` / `SMTP_PORT` | ✅ | SMTP server (STARTTLS) |
| `SMTP_EMAIL` / `SMTP_PASSWORD` | ✅ | SMTP sender credentials |

## 💳 Stripe Configuration

- Create **Pro** and **Premium** recurring prices and put their IDs in `PRO_PRICE_ID` / `PREMIUM_PRICE_ID`. They must match the price IDs in `FE/src/app/subscription/page.tsx`.
- Send these webhook events to `POST /stripe/webhook`:
  - `invoice.payment_succeeded`: activates and renews plans, refills the message allowance
  - `invoice.payment_failed`: emails the user; access continues while Stripe retries
  - `customer.subscription.updated`: tracks cancellations and undone cancellations
  - `customer.subscription.deleted`: moves the user to the Free tier
- Under **Billing → Revenue recovery**, set failed subscriptions to be **cancelled** after the final retry.

| Plan | Messages per billing period |
|---|---|
| Free | 0 |
| Pro | 100 |
| Premium | 350 |

## 📡 API Overview

| Area | Endpoints |
|---|---|
| Auth (`/users`) | `POST /signup/`, `POST /login`, `GET /protected/`, `GET /forget_password`, `POST /reset_password/{token}`, `POST /change-password`, `GET /verify-email/` |
| Chat | `POST /chat/start`, `POST /chat/message`, `GET /chat/history` |
| Restaurants | `GET /get_all_restaurants_name`, `GET /get_restaurant_data`, `GET /{id}/location`, `POST /search_restaurant` (rate-limited), `POST /feedback` |
| Questions | `GET /faqs`, `GET /faqs/{id}` |
| Billing (`/stripe`) | `POST /create-checkout-session`, `POST /change-plan`, `POST /cancel-subscription`, `GET /billing-details`, `GET /subscription/status`, `GET /success`, `POST /webhook` |
| Admin | `POST /admin/check-expired-subscriptions` (admin accounts only) |

Full request and response schemas are at `/docs` while the API is running.

## 🗄️ Database Migrations

```bash
alembic upgrade head                              # apply all migrations
alembic revision --autogenerate -m "describe change"   # create a migration after changing models
alembic check                                     # verify models and migrations are in sync
```

## 🐳 Docker

```bash
docker compose up --build
```

The API is exposed on `http://localhost:8000` and reads configuration from `BE/.env`.

## 📝 Notes

- The restaurant-search rate limiter and the subscription scheduler keep their state in memory, separately for each process. Run a single worker, or move them to Redis or a dedicated scheduler when scaling out.
- Behind a reverse proxy, start Uvicorn with `--proxy-headers --forwarded-allow-ips=<proxy ip>` so rate limiting sees real client IPs.

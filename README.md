# 💬 ReviewPulse

**AI-powered review intelligence for restaurant owners.**

ReviewPulse turns public customer reviews into actionable insight. Owners ask questions in plain English, such as *"What do customers complain about most?"* or *"How do we compare with Italian restaurants nearby?"*, and get answers grounded in real reviews of their restaurant and its local competitors.

> Designed, architected and built end to end by **[Arslan Rajpot](https://github.com/arslanrajpot)**: system design, AI/RAG pipeline, backend, payments, frontend, security and deployment.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)
![OpenAI](https://img.shields.io/badge/GPT--4o-412991?logo=openai&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-635BFF?logo=stripe&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js_15-000000?logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

---

## ✨ Features

- **Automated onboarding:** owners search for their restaurant by name and location. The platform pulls business details and up to 50 reviews for it from Google Maps, finds its 5 closest same-cuisine competitors, and indexes everything for search.
- **RAG-powered AI assistant:** a LangChain agent on GPT-4o answers questions from the indexed reviews first. It keeps the conversation context so follow-up questions work.
- **Guided question library:** a tree of expert-written questions, each with its own prompt template, output format and suggested follow-ups.
- **Personalised answers:** 👍/👎 feedback on answers shapes the tone, structure and depth of future answers for each user.
- **Analytics dashboard:** average rating, total public reviews, star-rating breakdown and highlights.
- **Subscription billing:** Stripe Checkout with Pro and Premium plans, monthly message allowances, prorated upgrades and cancellation at the end of the billing period.
- **Accounts:** signup, login, password change and a secure single-use password reset by email.

## 🏗️ Architecture

```
┌──────────────────────────────┐
│  Next.js 15 · React 19 · TS  │  FE/  App Router, Tailwind CSS 4, Recharts
└──────────────┬───────────────┘
               │ REST · JWT bearer auth · CORS restricted to configured frontend origins
┌──────────────▼───────────────────────────────────────────────┐
│                  FastAPI application (BE/)                   │
│  users │ restaurants │ subscription │ faq │ ai_assistants    │
│  routes → business logic → database access                   │
│  APScheduler (subscription lifecycle jobs)                   │
└───┬──────────┬──────────────┬───────────────┬────────────────┘
    │          │              │               │
PostgreSQL  Pinecone      OpenAI GPT-4o    Stripe · SerpAPI · SMTP
SQLAlchemy  vector index  LangChain agent  payments · data · email
Alembic
```

### How a question is answered

1. The user asks a question, either free text or from the guided question library.
2. The backend takes one message from the user's allowance in a single database update, so parallel requests can't overspend it.
3. The LangChain agent receives the question plus context: the restaurant's profile, the recent conversation and the user's feedback preferences.
4. The agent searches the **Pinecone** index of reviews first, and only falls back to the model's general knowledge if the data lacks an answer.
5. GPT-4o writes a Markdown answer, which the frontend renders after sanitizing it with DOMPurify.
6. If anything fails, the message is refunded automatically.

### Key design decisions

| Decision | Why |
|---|---|
| **RAG instead of fine-tuning** | Answers are grounded in each restaurant's live review data, and new restaurants can be added instantly with no retraining. |
| **Search the database before the model** | The verified review data is always searched first, which reduces made-up answers. |
| **Small local embedding model** | A 384-dimension Sentence-Transformers model (MiniLM) keeps embedding costs near zero, with a serverless Pinecone index for search. |
| **Stripe as the source of truth** | Webhooks drive every account-tier change, so the app stays consistent through renewals, payment retries, upgrades and cancellations. Events from an old subscription are ignored. |
| **Modular backend** | Each business area (users, restaurants, billing, FAQ, AI) is a separate module split into routes, business logic and database access, which keeps it testable and easy to extend. |

## 🔐 Security

- bcrypt password hashing and JWT access tokens with token types.
- Separate, short-lived, single-use password-reset tokens. The reset form doesn't reveal which emails have accounts.
- Each user's chats and feedback are kept separate, and admin endpoints are restricted to admin accounts.
- CORS and Stripe redirect URLs limited to the configured frontend origins, and checkout prices checked against an allow-list.
- The public restaurant-search endpoint is rate-limited per IP to protect paid third-party APIs.
- AI output is sanitized against XSS before rendering.

## 🧰 Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, APScheduler |
| AI / ML | OpenAI GPT-4o, LangChain (agents, tools, memory), Pinecone, Sentence-Transformers |
| Data | PostgreSQL, Pinecone vector index |
| Integrations | Stripe (Checkout, Subscriptions, Webhooks), SerpAPI (Google Maps), SMTP |
| Frontend | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 4, Recharts, marked, DOMPurify |
| DevOps | Docker, Docker Compose |

## 📁 Repository Structure

```
.
├── BE/                          # FastAPI backend
│   ├── app.py                   # App entry point: middleware, routers, chat endpoints
│   ├── ai_assistants/           # LangChain RAG agent and prompts
│   ├── rag_embeddings/          # Embedding and Pinecone indexing
│   ├── config_project/          # Settings and the Google Maps data pipeline
│   ├── users/                   # Auth, accounts, message allowance
│   ├── restaurants/             # Restaurant data, onboarding search, feedback
│   ├── subscription/            # Stripe checkout, plan changes, webhooks
│   ├── faq/                     # Guided question library (tree) and seed data
│   ├── alembic/                 # Database migrations
│   ├── scheduler.py             # Background subscription jobs
│   └── rate_limit.py            # Per-IP rate limiter
└── FE/                          # Next.js frontend
    └── src/
        ├── app/(auth)/          # Login, signup, password reset
        ├── app/(sidebar)/       # Dashboard, AI chat, settings, billing
        ├── app/subscription/    # Plans, checkout and upgrade
        └── service/             # API client
```

## 🚀 Getting Started

**Prerequisites:** Python 3.11, Node.js 18.18+, PostgreSQL, plus API keys for OpenAI, Pinecone, SerpAPI and Stripe.

```bash
git clone https://github.com/arslanrajpot/restaurant-reviews.git
cd restaurant-reviews
```

| Service | Guide | Default URL |
|---|---|---|
| Backend API | [BE/README.md](BE/README.md) | http://localhost:8000 (interactive docs at `/docs`) |
| Frontend | [FE/README.md](FE/README.md) | http://localhost:3000 |

## 👤 Author

**Arslan Rajpot**: Lead Engineer and Solution Architect
GitHub: [@arslanrajpot](https://github.com/arslanrajpot)

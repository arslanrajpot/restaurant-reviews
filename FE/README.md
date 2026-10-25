# 🥡 Review Munch: Frontend

Next.js web app for [Review Munch](../README.md): authentication, the AI review assistant, the analytics dashboard, and subscription management.

## 🛠️ Tech Stack

- **Framework:** Next.js 15 (App Router), React 19, TypeScript
- **Styling:** Tailwind CSS 4
- **Charts:** Recharts
- **Markdown rendering:** marked + DOMPurify (sanitized AI output)
- **Icons:** react-icons

## 📄 Pages

| Route | Description |
|---|---|
| `/login`, `/signup` | Authentication. Signup includes restaurant search and automatic onboarding |
| `/forget_password`, `/reset_password` | Password reset by email link |
| `/dashboard` | Rating overview, review totals and star-rating breakdown |
| `/review_agent` | AI assistant chat with guided questions and 👍/👎 feedback |
| `/setting`, `/setting/change_password`, `/setting/billing_details` | Account, password, invoices and cancellation |
| `/subscription`, `/subscription/success` | Plan selection, checkout, upgrades and payment confirmation |

## ⚙️ Setup

**Prerequisites:** Node.js 18.18+ and the [backend API](../BE/README.md) running.

```bash
cd FE
npm ci
```

Create or edit `FE/.env`:

```env
# Backend base URL. Must end with a trailing slash
NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000/
```

Add the frontend origin (e.g. `http://localhost:3000`) to the backend's `BASE_URL` or `CORS_ORIGINS`. Otherwise browsers will block the API requests.

## ▶️ Scripts

```bash
npm run dev     # development server at http://localhost:3000
npm run build   # production build
npm start       # serve the production build
npm run lint    # ESLint
```

## 🐳 Docker

```bash
docker compose up --build
```

The app is served on port 80. `NEXT_PUBLIC_*` variables are baked in at build time, so rebuild the image after changing `.env`.

## 📁 Structure

```
src/
├── app/
│   ├── (auth)/          # Login, signup, password reset
│   ├── (sidebar)/       # Dashboard, AI chat, settings (authenticated layout)
│   ├── subscription/    # Plans, checkout, success
│   └── _components/     # Shared layout components
├── hooks/               # e.g. useFeedback
├── service/api.tsx      # Typed API client (JWT auth, error handling)
├── shared/              # Shared UI (loader)
└── types/               # API types
```

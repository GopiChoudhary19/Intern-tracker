# Admin Setup

## 1. Required environment variables

Set these on the deployed services:

- API service:
  - `INTERN_TRACKER_DEMO_MODE=database`
  - `INTERN_TRACKER_ADMIN_TOKEN=<same-secret-you-store-in-render>`
  - `INTERN_TRACKER_CORS_ALLOWED_ORIGINS=https://internradar-web.onrender.com`
- Web service:
  - `NEXT_PUBLIC_API_BASE_URL=https://internradar.onrender.com/api/v1`
  - `INTERN_TRACKER_ADMIN_TOKEN=<same-secret-you-store-in-render>`
  - `INTERN_TRACKER_ADMIN_EMAILS=you@example.com` (comma-separated; only these signed-in users can open
    `/admin` or call the web app's `/api/admin/*` routes, everyone else is redirected or gets 403)

The API service also needs `INTERN_TRACKER_RESEND_API_KEY` so sign-in codes are emailed; without it, codes
are only shown when `INTERN_TRACKER_AUTH_DEBUG=true`, which must stay off in production.

Optional auth protection settings already supported:

- `INTERN_TRACKER_AUTH_DEBUG=false`
- `INTERN_TRACKER_AUTH_OTP_REQUEST_LIMIT=5`
- `INTERN_TRACKER_AUTH_OTP_REQUEST_WINDOW_MINUTES=15`

## 2. How to access admin data

### Web admin page

Open:

- `/admin`

If the deployed site shows `404 Not Found` for `/admin`:

- confirm the latest commit with `apps/web/app/admin/page.tsx` is deployed to the Render web service
- trigger a fresh deploy for `intern-tracker-web`
- if environment variables changed, redeploy both `intern-tracker-web` and `intern-tracker-api`
- verify the web service is still using `apps/web` as `rootDir`

This page shows:

- active users
- opportunity count
- saved and applied application counts
- stored user records

### API access

Use the `X-Admin-Token` header:

```bash
curl -H "X-Admin-Token: YOUR_SECRET_TOKEN" https://your-api-host/api/v1/admin/users
curl -H "X-Admin-Token: YOUR_SECRET_TOKEN" https://your-api-host/api/v1/admin/analytics/overview
```

## 3. What user data is stored

The app stores user data in PostgreSQL when database mode is enabled.

Stored data includes:

- `users`
  - email
  - phone
  - full name
  - college
  - degree
  - branch
  - graduation year
  - city
  - country
- `user_profiles`
  - bio
  - goals
  - preferred domains
  - preferred locations
  - preferred opportunity types
  - skills
  - GitHub URL
  - LinkedIn URL
  - resume URL
  - onboarding status
- `applications`
  - status
  - notes
  - follow-up dates
  - linked opportunity
- `auth_sessions`
  - session tokens
  - expiry
  - revoked state
- `auth_challenges`
  - OTP challenge records
  - hashed OTP codes
  - expiry and consumed timestamps

## 4. What you should do as admin

- Set a strong `INTERN_TRACKER_ADMIN_TOKEN`
- Keep `INTERN_TRACKER_AUTH_DEBUG=false` in production
- Keep `INTERN_TRACKER_DEMO_MODE=database`
- Review `/admin` regularly for new users and onboarding completion
- Rotate the admin token if it is ever exposed
- Back up the Postgres database
- Restrict who knows the admin token

## 5. Important remaining limitation

OTP generation, verification, throttling, and session handling are implemented.

Real email or SMS delivery is **not** connected yet. To make OTP login fully live, you still need to integrate an email or SMS provider and store its credentials in the API environment.

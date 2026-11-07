# Auth — Login & Protect (FastAPI + Supabase)

A FastAPI authentication API using Supabase Auth for signup, login, access-token verification, protected routes, and logout.

## Features
- `POST /auth/signup` — create a Supabase account (201)
- `POST /auth/login` — return access and refresh tokens (200)
- `POST /auth/logout` — revoke the presented session (204)
- `GET /public/info` — public endpoint
- `GET /protected/profile` — verified user profile
- `GET /protected/dashboard` — second protected endpoint
- Reusable FastAPI bearer-token dependency
- Swagger UI at `/docs`

## Files
`main.py`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md`, `screenshots/`

## 1. Supabase setup
Create a project at https://supabase.com/. Find its Project URL and public anon/publishable key under Project Settings → API. Do not use the `service_role` or secret key.

If email confirmation is enabled, confirm the signup email before logging in.

## 2. Environment
Copy `.env.example` to `.env` and enter your own values:

```env
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_ANON_OR_PUBLISHABLE_KEY
PORT=8000
```

Never commit `.env`, passwords, access tokens, refresh tokens, or secret keys. `.gitignore` excludes `.env`.

## 3. Install and run (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
If activation is blocked in PowerShell:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open http://localhost:8000/docs.

## 4. API reference
| Method | Endpoint | Auth? | Purpose |
|---|---|---:|---|
| POST | `/auth/signup` | No | Register |
| POST | `/auth/login` | No | Login and receive tokens |
| POST | `/auth/logout` | Yes | Revoke session |
| GET | `/public/info` | No | Public information |
| GET | `/protected/profile` | Yes | Verified profile |
| GET | `/protected/dashboard` | Yes | Protected example |
| GET | `/health` | No | Health check |

Signup/login body:
```json
{"email":"you@example.com","password":"a-strong-test-password"}
```

## 5. Test in Swagger
1. Call signup with an email and password.
2. Confirm the email if Supabase requires confirmation.
3. Call login and copy `access_token`.
4. Click **Authorize** in Swagger and paste the token only (do not type `Bearer `; Swagger adds it).
5. Call both protected endpoints; valid token should return 200.
6. Call a protected route without a token or with a modified token; it should return 401.
7. Call logout while authorized; it should return 204.

The Python SDK's `sign_out()` uses the SDK client's locally stored session. This API is stateless and receives a bearer token per request, so logout revokes the presented session using Supabase Auth's `/auth/v1/logout` endpoint with that token.

## 6. Status codes
| Case | Status |
|---|---:|
| Signup success | 201 |
| Login/public/protected read success | 200 |
| Logout success | 204 |
| Missing/invalid request fields | 400 |
| Wrong credentials | 401 |
| Missing/invalid/expired bearer token | 401 |

## 7. GitHub submission
Create a public repository and upload the source files, README, `.env.example`, and a genuine Swagger screenshot in `screenshots/`. Do not upload `.env` or any credentials.

A peer can clone the repo, create their own `.env`, install requirements, and run the documented command.

## Assignment checklist
- [ ] Supabase project and `.env` configured
- [ ] Signup/login tested against Supabase
- [ ] Public route returns 200
- [ ] Protected route verifies tokens and rejects invalid tokens
- [ ] Reusable auth dependency applied to protected routes
- [ ] Logout tested
- [ ] Swagger Authorize button and lock icons verified
- [ ] Screenshot added
- [ ] Public GitHub repo published with at least six meaningful commits
- [ ] No secrets committed

# AUI Secure — Secure Coding Demonstration Platform

## Project Description
DevSecOps CI/CD pipeline with integrated security gates across three deliverable phases. Includes GitHub Actions workflows, pre-commit hooks, and automated remediation scripts.

> **An interactive, full-stack security education platform** built for the course *Secure Software Design with Secure Coding Implementation*. Demonstrates real-world attack vectors and their defences through live, hands-on labs — not just slides.

![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![Security](https://img.shields.io/badge/Security-OWASP%20Top%2010-red)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-24-green?logo=node.js&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What Is This?

AUI Secure is a **dual-layer DevSecOps project** combining a fully-functional secure web application with an automated security CI/CD pipeline. The frontend is a dark-themed security dashboard (SPA) that lets you **interact with both the vulnerable and secure versions of each endpoint in real-time**, making it ideal for:

- 🎓 Course demonstrations and assignments
- 💼 Portfolio showcase (LinkedIn / GitHub)
- 🔬 Understanding OWASP Top 10 vulnerabilities hands-on
- 🏗️ Reference architecture for secure Flask applications

---

## Live Demo Features

### 🔬 Interactive Security Labs

| Lab | What You Can Do |
|-----|----------------|
| **SQL Injection** | Fire real payloads (`' OR 1=1 --`) against both a vulnerable endpoint (string-interpolated SQL) and a secure one (parameterised queries). See the actual SQL being generated live. |
| **XSS (Cross-Site Scripting)** | Inject `<script>alert()>` and `<img onerror>` payloads. Watch the attack endpoint reflect raw HTML while the secure endpoint strips tags and escapes entities. |
| **Password Hashing** | Enter any password and see two different `scrypt` hashes generated from the same input — demonstrating why salted hashing defeats rainbow tables. Includes a live password-strength meter. |
| **Security Headers** | View all 7 HTTP security headers (CSP, X-Frame-Options, HSTS, etc.) with severity ratings and plain-English explanations of what attack each prevents. |
| **CSRF Protection** | See a forged cross-site request form, then understand why `SameSite=Lax` cookies and CSRF tokens neutralise it. Displays your live session token. |
| **Rate Limiting** | Hammer the rate-limited endpoint and watch 200 responses flip to 429s. Live counter shows exactly when the limit trips. |
| **Account Lockout** | Register a user and brute-force it. See exponential backoff lockout kick in with progressive delays. |
| **Audit Trail** | Every action in the app (login, SQL query, XSS attempt, API call) is logged and visible in the live events feed — auto-refreshes every 5 seconds. |

### 🛡️ Security Mechanisms Implemented

```
Authentication          → werkzeug scrypt hashing, session rotation on login,
                          HttpOnly + SameSite=Lax cookies, configurable session lifetime

Account Lockout         → Exponential backoff (base_duration × 2^lockouts), max 24h,
                          progressive delay (up to 5s per attempt)

RBAC                    → @requires_auth / @requires_role("admin") decorators,
                          user and admin roles, API key authentication

Input Validation        → Username regex, password policy (8+ chars, upper/lower/digit/special),
                          HTML tag stripping (bleach), null-byte removal

SQL Injection           → Parameterized queries everywhere, dual endpoints for live comparison

XSS                     → html.escape() + tag stripping + CSP nonce-based script allowlist

CSRF                    → Session-bound tokens, secrets.compare_digest timing-safe compare

Security Headers        → CSP (nonce-based), X-Frame-Options: DENY, X-Content-Type-Options,
                          Referrer-Policy, Permissions-Policy, X-XSS-Protection, HSTS (prod)

Rate Limiting           → Flask-Limiter on auth endpoints, configurable per route

API Key Security        → SHA-256 hashed storage, Bearer token auth, key prefix display only,
                          last-used tracking, soft revocation

Audit Logging           → Every action logged: user, IP, user-agent, timestamp, success/fail
```

---

## Architecture

```
CdPipeline/
├── app/
│   ├── main.py          # App factory (create_app), session expiry, error handlers
│   ├── config.py        # All settings from env vars, warns on missing SECRET_KEY
│   ├── db.py            # SQLite init, per-request connection (Flask g), demo data seed
│   ├── auth.py          # Register, login (lockout + backoff), logout, session management
│   ├── items.py         # CRUD + search_secure / search_insecure dual endpoints
│   ├── api_keys.py      # Key generation, SHA-256 hashing, Bearer auth middleware
│   ├── dashboard.py     # Admin dashboard: user management, security stats
│   ├── lab.py           # All interactive lab endpoints (sqli, xss, hash, headers, etc.)
│   ├── rbac.py          # @requires_auth, @requires_role decorators
│   ├── security.py      # init_security: rate limiter, CSP nonce, all security headers
│   ├── audit.py         # log_action() — writes to audit_logs table, never raises
│   ├── validators.py    # ValidationError, validate_username/password, sanitize_text
│   └── templates/
│       ├── index.html   # SecureLab SPA (dark theme, 9 lab sections, vanilla JS)
│       └── dashboard.html  # Admin dashboard (user mgmt, audit log, security events)
│
├── tests/
│   ├── conftest.py      # Fixtures: temp DB per test, rate limiting disabled
│   ├── test_app.py      # Functional tests: auth, CRUD, headers, isolation
│   └── test_security.py # Security tests: SQLi payloads, XSS, lockout, RBAC, CSRF
│
├── .github/workflows/
│   └── devsecops.yml    # 5-stage CI/CD pipeline (tests → secrets → SAST → SCA → DAST)
│
├── .pre-commit-config.yaml  # black, bandit, pip-audit, gitleaks, file hygiene
├── remediate.py             # Auto-patches vulnerable deps and opens a PR
└── requirements.txt
```

---

## CI/CD Security Pipeline

Every `git push` triggers a **5-stage security gauntlet** in GitHub Actions:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Stage 1 │ Build & Tests     │ pytest — functional + security tests  │
│  Stage 2 │ Secret Scanning   │ gitleaks — blocks hardcoded secrets   │
│  Stage 3 │ SAST              │ Bandit — static code security analysis│
│  Stage 4 │ SCA + Auto-fix    │ pip-audit → remediate.py → opens PR   │
│  Stage 5 │ DAST (push only)  │ OWASP ZAP baseline scan vs live app   │
└─────────────────────────────────────────────────────────────────────┘
```

**Auto-remediation**: When `pip-audit` finds vulnerable dependencies, `remediate.py` automatically updates `requirements.txt` and opens a Pull Request — no manual intervention needed.

**Pre-commit hooks** run the same checks locally before any commit reaches GitHub:
- `black` — code formatting
- `bandit` — static security analysis
- `pip-audit` — dependency vulnerability scan
- `gitleaks` — secret detection
- File hygiene: YAML/JSON validity, merge conflict markers, private key detection

---

## Getting Started

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/CdPipeline.git
cd CdPipeline

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Running the Application

```bash
# Development mode (SECURE_MODE=true by default)
python run.py

# Enable insecure demo endpoints for lab demonstrations
set SECURE_MODE=false && python run.py    # Windows
# SECURE_MODE=false python run.py          # Linux/macOS
```

Open **http://localhost:5000** in your browser.

### Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | *(random, warns if missing)* | Flask session signing key |
| `SECURE_MODE` | `true` | Set `false` to enable vulnerable endpoints for demos |
| `MAX_LOGIN_ATTEMPTS` | `5` | Failed logins before lockout |
| `LOCKOUT_DURATION_SECONDS` | `300` | Base lockout duration (exponential backoff applied) |
| `DATABASE_PATH` | `securelab.db` | SQLite database file path |
| `FLASK_ENV` | `development` | Set `production` to enable HSTS and Secure cookie flag |

### Running Tests

```bash
pytest tests/ -v
```

---

## Security Lab Walkthrough

### SQL Injection Demo

1. Navigate to **SQL Injection Lab** in the sidebar
2. Click the `' OR '1'='1` payload chip
3. Hit **Attack (Vulnerable)** — see all products returned regardless of search
4. Switch to **Defend (Secure)** — same payload, zero results, parameterised query shown

> **Why it works**: The attack endpoint builds SQL via f-string interpolation. The defend endpoint uses `db.execute(sql, (f"%{q}%",))` — the database driver escapes the parameter, making injection impossible.

### XSS Demo

1. Navigate to **XSS Lab**
2. Click the `<script>alert('XSS')</script>` payload chip
3. **Attack response**: raw HTML returned (`vulnerable: true`)
4. **Defend response**: tags stripped to empty string, HTML entities escaped

> **Defence layers**: (1) `bleach` strips all tags, (2) `html.escape()` converts `<>` to entities, (3) CSP header only executes scripts with a valid server-issued nonce.

### Password Hashing Demo

1. Navigate to **Auth Security Lab**
2. Enter any password and click **Generate Hash**
3. Observe: two hashes from the same password are completely different (random salt)
4. Both verify as `true` with `check_password_hash`

---

## Key Security Design Decisions

**Why SQLite?** — Simplicity for demonstration. All parameterised query patterns are identical for PostgreSQL/MySQL.

**Why SECURE_MODE toggle?** — The insecure endpoints are intentionally included for education but guarded by a server-side flag. Deploying with `SECURE_MODE=true` (default) makes the app production-safe while keeping the vulnerable code available for controlled demos.

**Why no frontend framework?** — Zero external JS dependencies means zero supply-chain risk from npm. The entire SPA is vanilla JS in one `<script nonce="...">` block, which also makes the CSP policy trivially correct.

**Why scrypt over bcrypt?** — werkzeug 3.x defaults to scrypt, which is memory-hard and resists GPU-based attacks better than bcrypt. The app uses werkzeug's `generate_password_hash` / `check_password_hash` directly, so the algorithm can be upgraded transparently.

---

## OWASP Top 10 Coverage

| # | Vulnerability | Demonstrated | Mitigated |
|---|--------------|:------------:|:---------:|
| A01 | Broken Access Control | ✅ | ✅ RBAC + @requires_role |
| A02 | Cryptographic Failures | ✅ | ✅ scrypt hashing, HttpOnly cookies |
| A03 | Injection (SQLi) | ✅ | ✅ Parameterised queries |
| A04 | Insecure Design | ✅ | ✅ SECURE_MODE gating |
| A05 | Security Misconfiguration | ✅ | ✅ Security headers, CSP |
| A06 | Vulnerable Components | ✅ | ✅ pip-audit + auto-remediation |
| A07 | Auth & Session Failures | ✅ | ✅ Lockout, session rotation |
| A08 | Software Integrity Failures | ✅ | ✅ gitleaks, secret scanning |
| A09 | Logging & Monitoring Failures | ✅ | ✅ Audit trail, live events |
| A10 | Server-Side Request Forgery | — | ✅ No outbound requests |

---

## Course Context

Built for **Secure Software Design with Secure Coding Implementation** — demonstrating that security is not a feature you bolt on at the end, but an architectural concern threaded through every layer:

- **Design phase**: Threat modelling, SECURE_MODE toggle, RBAC schema
- **Coding phase**: Validators, parameterised queries, CSP nonce pattern
- **Testing phase**: Security-specific pytest suite (SQLi payloads, lockout, CSRF)
- **CI/CD phase**: Automated SAST, SCA, secret scanning, DAST on every push

---

## License

MIT — free to use, modify, and share with attribution.

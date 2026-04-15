# 🎬 AUI Secure — Complete Demo Guide

**Complete walkthrough to demonstrate the AUI Secure platform from start to finish.**

---

## 📋 Demo Checklist

- [ ] Environment setup
- [ ] Start the Flask app
- [ ] Register a test account
- [ ] Login
- [ ] SQL Injection Lab
- [ ] XSS Lab
- [ ] Password Hashing Lab
- [ ] Security Headers Lab
- [ ] CSRF Protection Lab
- [ ] Rate Limiting Lab
- [ ] Account Lockout Lab
- [ ] Audit Trail Lab
- [ ] Toggle SECURE_MODE for insecure endpoints
- [ ] Admin Dashboard
- [ ] Security stats & monitoring

---

## 🚀 Part 1: Setup & Launch (5 minutes)

### Step 1: Open Terminal & Navigate
```powershell
cd C:\Users\dumbutthehe\Desktop\CdPipeline
```

### Step 2: Activate Virtual Environment
```powershell
.\.venv\Scripts\activate
```
**Expected Output:**
```
(.venv) PS C:\Users\dumbutthehe\Desktop\CdPipeline>
```

### Step 3: Start Flask App
```powershell
python run.py
```

**Expected Output:**
```
 * Serving Flask app 'app.main'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Step 4: Open in Browser
Navigate to: **`http://localhost:5000`**

**What You'll See:**
- 🔐 **AUI Secure** header with lock icon
- "Secure Coding Demos" subtitle
- ✅ **● SECURE MODE** indicator (green)
- Dark-themed dashboard
- Sidebar with all lab categories

---

## 🔐 Part 2: Authentication (3 minutes)

### Step 1: Register a Test Account
**On the homepage, look for Register section or click "Auth & Session"**

Enter:
- **Username:** `demouser`
- **Password:** `Demo@Password123` (must be 8+ chars, uppercase, lowercase, digit, special char)
- **Confirm:** Same password

Click **Register**

**What Happens:**
- ✅ Password hashed with scrypt (random salt)
- ✅ User created in database
- ✅ Account lockout mechanism initialized
- ✅ Audit log entry created

### Step 2: Login with Credentials
Use the same username & password from registration:
- **Username:** `demouser`
- **Password:** `Demo@Password123`

Click **Login**

**What Happens:**
- ✅ Credential verification (scrypt hash comparison)
- ✅ Session created with HttpOnly cookie
- ✅ Session rotation triggered
- ✅ Logged in audit trail

### Step 3: Verify Login Success
After login, you should see:
- ✅ Your username displayed in the app
- ✅ All lab sections unlocked
- ✅ User dashboard/profile option
- ✅ Logout button visible

---

## 🔬 Part 3: Security Labs (15 minutes)

### Lab 1️⃣: SQL Injection (4 minutes)

**Location:** Sidebar → "Injection" or "SQL Injection Lab"

#### A. Attack Endpoint (Insecure)
1. Click **"Attack (Vulnerable)"** button
2. In the input field, enter: `' OR '1'='1`
3. Click **Execute**

**What Happens:**
```
❌ VULNERABLE — String interpolation!
SQL Generated: SELECT * FROM products WHERE name LIKE '%' OR '1'='1%'
Result: ALL PRODUCTS RETURNED (injection successful!)
```
- Shows the SQL being generated
- Shows how many rows bypass the intended filter
- Explains the vulnerability

#### B. Defend Endpoint (Secure)
1. Click **"Defend (Secure)"** button
2. Try the same payload: `' OR '1'='1`
3. Click **Execute**

**What Happens:**
```
✅ SECURE — Parameterized queries!
SQL Template: SELECT * FROM products WHERE name LIKE ?
Parameters: ["%' OR '1'='1%"]
Result: 0 ROWS (injection blocked, treated as literal string)
```
- Shows parameterized query template
- Shows bound parameters separately
- Explains why injection is impossible

**Key Learning:**
> Parameterized queries escape special characters, making injection impossible.

---

### Lab 2️⃣: XSS (Cross-Site Scripting) (3 minutes)

**Location:** Sidebar → "XSS Lab" or "Injection"

#### A. Attack Endpoint (Insecure)
1. Click **"Attack (Vulnerable)"** button
2. In the content field, paste: `<script>alert('XSS')</script>`
3. Click **Execute**

**What Happens:**
```
❌ VULNERABLE — Raw HTML reflection!
Raw Output: <script>alert('XSS')</script>
Result: Script would execute if rendered to DOM
vulnerable: true
```
- Shows the raw unescaped HTML
- Explains how JavaScript executes
- Demonstrates the attack

#### B. Defend Endpoint (Secure)
1. Click **"Defend (Secure)"** button
2. Try the same payload: `<script>alert('XSS')</script>`
3. Click **Execute**

**What Happens:**
```
✅ SECURE — Multiple layers!
1. Tags stripped: (empty string)
2. HTML escaped: &lt;script&gt;alert('XSS')&lt;/script&gt;
3. CSP nonce enforced: script tags without valid nonce rejected
Result: Nothing executes, text safely displayed
vulnerable: false
```

**Key Learning:**
> Defense-in-depth: Strip tags + HTML escape + CSP nonce = XSS impossible.

---

### Lab 3️⃣: Password Hashing (2 minutes)

**Location:** Sidebar → "Auth & Session" or "Auth Security"

1. Find the **Password Hashing Demo** section
2. Enter any password: `TestPassword123`
3. Click **Generate Hash**

**What You'll See:**
```
Hash 1: scrypt:32768:8:1$...[64 chars]...
Hash 2: scrypt:32768:8:1$...[64 chars]... (DIFFERENT!)

✅ Same password, completely different hashes (random salt)
✅ Verify: Both match the original password
✗ Wrong password: Hash mismatch
```

**Key Learning:**
> Salted hashing defeats rainbow tables. Each hash is unique, but always verifiable.

---

### Lab 4️⃣: Security Headers (1 minute)

**Location:** Sidebar → "Security Headers" or "Headers Info"

1. Click **View Security Headers**

**What You'll See:**
```
✅ CSP (Content-Security-Policy)
   Prevents inline scripts, allows only server-issued nonces
   Severity: CRITICAL

✅ X-Frame-Options: DENY
   Prevents clickjacking attacks
   Severity: HIGH

✅ X-Content-Type-Options: nosniff
   Prevents MIME type sniffing
   Severity: MEDIUM

✅ Referrer-Policy: strict-origin-when-cross-origin
   Controls referrer information leakage
   Severity: MEDIUM

✅ Permissions-Policy
   Restricts browser features (camera, microphone, etc.)
   Severity: MEDIUM

✅ HSTS (HTTP Strict-Transport-Security)
   Forces HTTPS connections
   Severity: HIGH (production only)
```

**Key Learning:**
> Security headers add defense layers at the HTTP level.

---

### Lab 5️⃣: CSRF Protection (1 minute)

**Location:** Sidebar → "CSRF Lab" or "Session Security"

1. Click **View CSRF Info**
2. Observe your current session CSRF token
3. Click **Check Session Cookie**

**What You'll See:**
```
Your Session Cookie:
sessionid=abc123...def456
Flags: HttpOnly, SameSite=Lax, Secure (prod only)

CSRF Token:
eyJ1c2VyX2lkIjog...MjA=

Attack Attempt:
<form method="POST" action="https://evil.com/transfer">
  <input type="hidden" name="amount" value="1000">
</form>

❌ WITHOUT CSRF token: Request BLOCKED
✅ WITH CSRF token: Request ALLOWED (but verified secure)
```

**Key Learning:**
> CSRF tokens + SameSite cookies prevent forged requests.

---

### Lab 6️⃣: Rate Limiting (2 minutes)

**Location:** Sidebar → "Rate Limiting Lab"

1. Click **Test Rate Limit**
2. Spam the **"Make Request"** button rapidly (10+ times)

**What Happens:**
```
Request 1-5:   ✅ 200 OK
Request 6-7:   ⚠️ 429 Too Many Requests
Request 8-10:  ⚠️ 429 Too Many Requests (Rate limit: 5 per minute)

Live Counter:
Requests Made: 10
Rate Limited: 5
Retry After: 45 seconds
```

**Key Learning:**
> Rate limiting stops brute force and DDoS attacks.

---

### Lab 7️⃣: Account Lockout (2 minutes)

**Location:** Sidebar → "Account Security" or "Auth & Session"

1. Click **Simulate Lockout**
2. Enter wrong password **5 times** rapidly

**What Happens:**
```
Attempt 1: ❌ Invalid password (4 attempts remaining)
Attempt 2: ❌ Invalid password (3 attempts remaining)
Attempt 3: ❌ Invalid password (2 attempts remaining)
Attempt 4: ❌ Invalid password (1 attempt remaining)
Attempt 5: ❌ Invalid password — ACCOUNT LOCKED

Lockout Duration: 5 minutes
Exponential Backoff: 2^5 = 32 seconds minimum wait

If you try again in 30 seconds:
⏳ Account locked. Wait 2 more seconds before retrying.
```

**Key Learning:**
> Exponential backoff defeats brute force by making each attempt progressively slower.

---

### Lab 8️⃣: Audit Trail (2 minutes)

**Location:** Sidebar → "Audit Trail" or "Monitoring"

1. Click **View Audit Events** (or bottom-right Events Panel)
2. Trigger some actions:
   - Try to login with wrong password
   - Create a new item
   - Search for something
   - Try an injection payload

**What You'll See:**
```
EVENT 1: LOGIN_FAILED
  Time: 2026-05-04 00:35:42
  User: demouser
  IP: 127.0.0.1
  Reason: Invalid password
  Success: false

EVENT 2: ITEM_CREATED
  Time: 2026-05-04 00:36:00
  User: demouser
  Item: "Test Product"
  Success: true

EVENT 3: LAB_SQLI_ATTEMPT
  Time: 2026-05-04 00:36:15
  User: demouser
  Payload: ' OR '1'='1
  Endpoint: /lab/sqli/attack
  Success: false (blocked by SECURE_MODE)

[Live refresh every 5 seconds]
```

**Key Learning:**
> Audit logging provides accountability and forensic capability.

---

## 🔓 Part 4: SECURE_MODE Toggle Demo (5 minutes)

### What is SECURE_MODE?

- **`SECURE_MODE=true` (Default)** — Insecure endpoints return 403 blocked
- **`SECURE_MODE=false`** — Insecure endpoints exposed for demonstrations

### Demo: Enable Insecure Endpoints

#### Step 1: Stop Flask App
Press `CTRL+C` in the terminal

```
KeyboardInterrupt
(.venv) PS C:\Users\dumbutthehe\Desktop\CdPipeline>
```

#### Step 2: Start with SECURE_MODE=false
```powershell
$env:SECURE_MODE="false"
python run.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
```

#### Step 3: Refresh Browser
Go back to `http://localhost:5000`

**What Changes:**
- Mode indicator changes: **● INSECURE MODE** (red/orange)
- Warning banner appears: "⚠️ Dangerous vulnerable endpoints are exposed"
- Lab buttons now show: **[ATTACK - Vulnerable!]** and *[Defend - Secure]*

#### Step 4: Run Insecure Labs

**SQL Injection Attack (Now Works!):**
1. Go to SQL Injection Lab
2. Click **ATTACK - Vulnerable!**
3. Enter: `' OR '1'='1`
4. See all products returned (injection successful!)

**XSS Attack (Now Works!):**
1. Go to XSS Lab
2. Click **ATTACK - Vulnerable!**
3. Enter: `<img src=x onerror="alert('XSS')">`
4. See raw HTML reflection in the response

#### Step 5: Re-enable SECURE_MODE

```powershell
$env:SECURE_MODE="true"
```

Press `CTRL+C` and restart:
```powershell
python run.py
```

Refresh browser — insecure endpoints blocked again, mode returns to **● SECURE MODE**

**Key Learning:**
> SECURE_MODE allows shipping vulnerable code safely by gating it server-side.

---

## 📊 Part 5: Admin Dashboard (3 minutes)

**Location:** Top-right menu → "Admin" or "Dashboard"

### What You'll See:

```
📈 Security Statistics
├─ Total Users: 5
├─ Active Sessions: 2
├─ Recent Events: 47
├─ Locked Accounts: 0
└─ Security Score: 95/100

👥 User Management
├─ demouser (created 5 min ago)
├─ testadmin (created yesterday)
└─ [Add User] [Delete User] [Reset Password]

📋 Recent Audit Events
├─ 00:36:42 LOGIN_FAILED (demouser, 127.0.0.1)
├─ 00:36:15 LAB_SQLI_ATTACK (demouser, payload: ' OR '1'='1)
├─ 00:35:58 ITEM_CREATED (demouser, item: Test Product)
└─ [View All Events]

🔒 Security Alerts
├─ ⚠️ 3 failed login attempts (demouser)
├─ ✅ No hardcoded secrets detected
├─ ✅ All dependencies up-to-date
└─ ✅ SSL/TLS enabled (prod only)
```

### Admin Actions:
1. **View User Details** — Click on any user to see:
   - Account creation date
   - Last login time
   - Login attempts
   - API keys assigned
   - Audit events

2. **Reset Password** — Demonstrate password reset flow

3. **Manage API Keys** — Show key generation and revocation

---

## 🎯 Part 6: Code Behind the Scenes (5 minutes)

### Show the Key Files:

#### SQL Injection Lab Code
Open: `app/lab.py` → Search for `sqli_attack` and `sqli_defend`

**Attack Version:**
```python
# VULNERABLE: direct string interpolation into SQL
sql = f"SELECT * FROM products WHERE name LIKE '%{q}%'"
```

**Defend Version:**
```python
# SECURE: parameterized query
sql_template = "SELECT * FROM products WHERE name LIKE ?"
db.execute(sql_template, (f"%{q}%",))
```

**Explanation:**
> In the attack version, the user input `q` is directly inserted into the SQL string. An attacker can break out with quotes and inject new SQL. In the defend version, the parameter is separated from the query, so the database driver always treats it as a string literal.

#### XSS Protection Code
Open: `app/validators.py` → Search for `sanitize_text`

```python
def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Strip all HTML tags and null bytes."""
    cleaned = bleach.clean(text, tags=[], strip=True)
    cleaned = cleaned.replace('\x00', '')
    return cleaned[:max_length]
```

**Explanation:**
> `bleach.clean()` removes all HTML tags. `html.escape()` converts `<>` to entities. Combined with CSP nonce validation, scripts can't execute.

#### Security Headers Code
Open: `app/security.py` → Search for `init_security`

```python
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = f"default-src 'self'; script-src 'nonce-{nonce}'"
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
```

**Explanation:**
> Security headers tell the browser how to behave. CSP with nonce prevents inline scripts. X-Frame-Options prevents clickjacking.

---

## 📈 Part 7: Architecture Overview (3 minutes)

### Show the Project Structure:
```
AUI Secure/
├── app/
│   ├── main.py          ← Flask app factory
│   ├── lab.py           ← Security lab endpoints (8 labs)
│   ├── auth.py          ← Login, lockout, session
│   ├── db.py            ← Database setup
│   ├── security.py      ← Headers, CORS, CSP, rate limiting
│   ├── validators.py    ← Input validation & sanitization
│   └── templates/       ← Dark-themed SPA
│
├── tests/
│   ├── test_app.py      ← Functional tests
│   └── test_security.py ← Security tests (SQLi, XSS, etc.)
│
├── .github/workflows/
│   └── devsecops.yml    ← CI/CD pipeline (5 stages)
│
└── requirements.txt     ← Flask, pytest, bandit, pip-audit, etc.
```

**Talk Points:**
- "Each lab endpoint has two versions: vulnerable and secure"
- "SECURE_MODE toggle gates the vulnerable endpoints"
- "All dependencies are scanned for vulnerabilities in CI/CD"
- "Security tests verify that exploits are blocked"

---

## 🔄 Part 8: CI/CD Pipeline (2 minutes)

### Show GitHub Actions Pipeline:
Open: `.github/workflows/devsecops.yml`

**Explain the 5 Stages:**

```
Stage 1: Build & Tests       ✅ Run pytest (functional + security tests)
    ↓
Stage 2: Secret Scanning     ✅ Gitleaks (blocks hardcoded secrets)
    ↓
Stage 3: SAST                ✅ Bandit (static code analysis)
    ↓
Stage 4: SCA + Auto-fix      ✅ pip-audit + remediate.py
    ↓
Stage 5: DAST (on push)      ✅ OWASP ZAP baseline scan
```

**Key Point:**
> "Every `git push` triggers this security gauntlet. Code can't reach production without passing all 5 security gates."

---

## 🎓 Part 9: OWASP Top 10 Summary (2 minutes)

**Show Coverage Table:**

| # | Vulnerability | Lab | Demonstrated |
|---|-------------|-----|:---:|
| A01 | Broken Access Control | RBAC | ✅ |
| A02 | Cryptographic Failures | Hashing | ✅ |
| A03 | Injection | SQLi | ✅ |
| A04 | Insecure Design | SECURE_MODE | ✅ |
| A05 | Security Misconfiguration | Headers | ✅ |
| A06 | Vulnerable Components | CI/CD | ✅ |
| A07 | Auth & Session Failures | Lockout | ✅ |
| A08 | Software Integrity Failures | Gitleaks | ✅ |
| A09 | Logging & Monitoring | Audit | ✅ |
| A10 | SSRF | Design | ✅ |

**Takeaway:**
> "AUI Secure demonstrates all 10 OWASP Top 10 vulnerabilities and their defenses."

---

## 🎉 Demo Conclusion (2 minutes)

### Key Takeaways:

1. **Security is Architectural** — Built into every layer, not bolted on
2. **Defense-in-Depth** — Multiple layers (input validation + parameterized queries + CSP)
3. **Automation Wins** — CI/CD gates catch vulnerabilities before deployment
4. **Education Matters** — Understanding vulnerabilities is the first step to fixing them
5. **Safe by Default** — SECURE_MODE=true makes the app production-ready while keeping vulnerable code available for learning

### Where to Go From Here:

- **Portfolio:** Push this to GitHub, showcase on LinkedIn
- **Learning:** Modify the labs to add your own vulnerabilities
- **Teaching:** Use SECURE_MODE=false in a classroom environment
- **Production:** Deploy with SECURE_MODE=true + real secrets + HTTPS

---

## ⏱️ Total Demo Time

| Part | Time |
|------|------|
| Setup & Launch | 5 min |
| Authentication | 3 min |
| Security Labs | 15 min |
| SECURE_MODE Toggle | 5 min |
| Admin Dashboard | 3 min |
| Code Behind Scenes | 5 min |
| Architecture | 3 min |
| CI/CD Pipeline | 2 min |
| OWASP Coverage | 2 min |
| Conclusion | 2 min |
| **TOTAL** | **45 minutes** |

---

## 💡 Demo Tips

1. **Keep Terminal Visible** — Show the Flask server logs when actions happen
2. **Explain Before Showing** — Explain what you're about to demo before executing
3. **Use Browser DevTools** — Show Network tab for security headers, Application tab for cookies
4. **Live Interaction** — Let audience try labs themselves
5. **Compare Side-by-Side** — Attack vs Defend makes the difference crystal clear
6. **Show Failures First** — Insecure endpoint shows the vulnerability, secure endpoint shows the fix
7. **Emphasize the Toggle** — SECURE_MODE is the "secret sauce" that makes it safe by default

---

## 🚨 Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 5000 already in use | Change port: `$env:FLASK_PORT=5001` |
| Database locked | Delete `app.db`, restart app |
| "No module named..." | Run `pip install -r requirements.txt` |
| SECURE_MODE not changing | Restart Flask app after `$env:SECURE_MODE=...` |
| Styles not loading | Hard refresh: `Ctrl+Shift+R` (Clear cache) |

---

**Ready to demo? Break a leg! 🎬**

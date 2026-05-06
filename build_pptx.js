// AUI Secure — Presentation Builder
process.env.NODE_PATH = "C:/Users/dumbutthehe/AppData/Roaming/npm/node_modules";
require("module").Module._initPaths();

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "AUI Secure — Secure Coding Demonstration Platform";

const W = 10, H = 5.625;

// ── PALETTE ───────────────────────────────────────────────────────────────────
const C = {
  BG:           "0A0E1A",
  CARD:         "0E1627",
  CARD2:        "111D34",
  CARD3:        "162040",
  BORDER:       "1C3054",
  BORDER_CYAN:  "005577",
  CYAN:         "00D4FF",
  CYAN_DIM:     "007799",
  GREEN:        "00FF88",
  GREEN_DIM:    "008844",
  RED:          "FF4757",
  RED_DIM:      "881122",
  ORANGE:       "FF9500",
  YELLOW:       "FFD700",
  PURPLE:       "9B59B6",
  PURPLE_DIM:   "4A235A",
  WHITE:        "FFFFFF",
  LIGHT:        "A8B8CC",
  GRAY:         "5A6880",
};

// ── SHADOW FACTORIES ──────────────────────────────────────────────────────────
const sh    = ()  => ({ type: "outer", color: "000000", blur: 10, offset: 4, angle: 135, opacity: 0.7 });
const glw   = (c) => ({ type: "outer", color: c,        blur: 20, offset: 0, angle: 0,   opacity: 0.45 });
const glwSm = (c) => ({ type: "outer", color: c,        blur: 10, offset: 0, angle: 0,   opacity: 0.35 });

// ── HELPERS ───────────────────────────────────────────────────────────────────
function addDotGrid(s) {
  for (let x = 1.0; x < W - 0.5; x += 1.25) {
    for (let y = 0.55; y < H - 0.3; y += 0.85) {
      s.addShape(pres.shapes.OVAL, {
        x: x - 0.02, y: y - 0.02, w: 0.04, h: 0.04,
        fill: { color: "182A44" }, line: { color: "182A44", width: 0 }
      });
    }
  }
}

function addGridLines(s) {
  for (let x = 1.25; x < W; x += 1.25) {
    s.addShape(pres.shapes.LINE, { x, y: 0, w: 0, h: H,
      line: { color: "0D1C30", width: 0.75 } });
  }
  for (let y = 0.85; y < H; y += 0.85) {
    s.addShape(pres.shapes.LINE, { x: 0, y, w: W, h: 0,
      line: { color: "0D1C30", width: 0.75 } });
  }
}

// 3D raised card
function card3d(s, x, y, w, h, opts = {}) {
  const fill   = opts.fill   || C.CARD;
  const border = opts.border || C.BORDER;
  // Offset shadow rect
  s.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.08, y: y + 0.08, w, h,
    fill: { color: "000000" }, line: { color: "000000", width: 0 }
  });
  const def = { x, y, w, h, fill: { color: fill }, line: { color: border, width: 1 } };
  def.shadow = opts.glow ? glw(opts.glow) : sh();
  s.addShape(pres.shapes.RECTANGLE, def);
}

function accentBar(s, x, y, h, color) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.07, h,
    fill: { color }, line: { color, width: 0 } });
}

function cornerAccents(s) {
  s.addShape(pres.shapes.LINE, { x: 0.12, y: 0.12, w: 0.4, h: 0,
    line: { color: C.CYAN, width: 1.5 } });
  s.addShape(pres.shapes.LINE, { x: 0.12, y: 0.12, w: 0, h: 0.4,
    line: { color: C.CYAN, width: 1.5 } });
  s.addShape(pres.shapes.LINE, { x: W - 0.52, y: H - 0.12, w: 0.4, h: 0,
    line: { color: C.CYAN, width: 1.5 } });
  s.addShape(pres.shapes.LINE, { x: W - 0.12, y: H - 0.52, w: 0, h: 0.4,
    line: { color: C.CYAN, width: 1.5 } });
}

function addPill(s, x, y, w, h, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h,
    fill: { color }, line: { color, width: 0 }, rectRadius: h / 2,
    shadow: glwSm(color) });
}

function slideTitle(s, text, y = 0.18) {
  s.addText(text, { x: 0.5, y, w: 9, h: 0.45,
    fontSize: 26, fontFace: "Arial Black", bold: true, color: C.WHITE,
    charSpacing: 3, margin: 0 });
}

function titleLine(s, x2, color = C.CYAN, y = 0.67) {
  s.addShape(pres.shapes.LINE, { x: 0.5, y, w: x2, h: 0,
    line: { color, width: 2 } });
}

// ── SLIDE 1 — TITLE ───────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  addDotGrid(s);
  cornerAccents(s);

  // Glow orb behind title
  s.addShape(pres.shapes.OVAL, { x: 2.5, y: 0.85, w: 5, h: 3.2,
    fill: { color: "00204A", transparency: 40 }, line: { color: "00204A", width: 0 } });

  // Course label
  s.addText("SECURE SOFTWARE DESIGN WITH SECURE CODING IMPLEMENTATION", {
    x: 0.5, y: 0.35, w: 9, h: 0.28,
    fontSize: 7.5, fontFace: "Consolas", bold: true, color: C.GRAY,
    align: "center", charSpacing: 3, margin: 0
  });

  // Main title
  s.addText("AUI SECURE", {
    x: 0.5, y: 0.68, w: 9, h: 1.35,
    fontSize: 72, fontFace: "Arial Black", bold: true, color: C.WHITE,
    align: "center", charSpacing: 6, margin: 0,
    shadow: glw(C.CYAN)
  });

  // Subtitle
  s.addText("A Full-Stack DevSecOps Security Education Platform", {
    x: 0.5, y: 2.08, w: 9, h: 0.52,
    fontSize: 20, fontFace: "Calibri", color: C.CYAN,
    align: "center", margin: 0
  });

  // Separator dots
  for (let i = 0; i < 5; i++) {
    s.addShape(pres.shapes.OVAL, { x: 4.55 + i * 0.22, y: 2.72, w: 0.08, h: 0.08,
      fill: { color: C.CYAN_DIM }, line: { color: C.CYAN_DIM, width: 0 } });
  }

  // Stat pills
  const pills = [
    { label: "8 Live Labs",   color: C.CYAN   },
    { label: "OWASP Top 10", color: C.GREEN  },
    { label: "5-Stage CI/CD",color: C.ORANGE },
  ];
  pills.forEach((p, i) => {
    const px = 1.55 + i * 2.5;
    addPill(s, px, 3.05, 1.9, 0.42, p.color);
    s.addText(p.label, { x: px, y: 3.05, w: 1.9, h: 0.42,
      fontSize: 12, fontFace: "Calibri", bold: true, color: C.BG,
      align: "center", valign: "middle", margin: 0 });
  });

  // Tech stack line
  s.addText("Python · Flask · SQLite · GitHub Actions · OWASP ZAP · Bandit · gitleaks · pip-audit", {
    x: 0.5, y: 3.7, w: 9, h: 0.3,
    fontSize: 9, fontFace: "Consolas", color: C.GRAY, align: "center", margin: 0
  });

  // Year
  s.addText("2026", { x: 0.5, y: H - 0.34, w: 9, h: 0.24,
    fontSize: 9, fontFace: "Calibri", color: C.GRAY, align: "center", margin: 0 });
}

// ── SLIDE 2 — THE PROBLEM ─────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  cornerAccents(s);

  slideTitle(s, "THE PROBLEM");
  titleLine(s, 4.0, C.RED);

  // Left — problems
  card3d(s, 0.35, 1.0, 4.4, 4.0, { fill: C.CARD, border: "3A1525" });
  accentBar(s, 0.35, 1.0, 4.0, C.RED);

  s.addText("Security is broken", { x: 0.55, y: 1.1, w: 4.0, h: 0.35,
    fontSize: 15, fontFace: "Calibri", bold: true, color: C.RED, margin: 0 });

  const problems = [
    "Security bolted on AFTER development — too late",
    "OWASP Top 10 vulnerabilities still widespread in 2026",
    "Devs don't understand attacks they've never seen",
    "Static slides don't build real security intuition",
    "CI/CD pipelines rarely include automated security checks",
  ];
  problems.forEach((p, i) => {
    const py = 1.58 + i * 0.65;
    s.addShape(pres.shapes.OVAL, { x: 0.52, y: py + 0.04, w: 0.28, h: 0.28,
      fill: { color: C.RED_DIM }, line: { color: C.RED, width: 1 } });
    s.addText("X", { x: 0.52, y: py + 0.04, w: 0.28, h: 0.28,
      fontSize: 10, fontFace: "Arial", bold: true, color: C.RED,
      align: "center", valign: "middle", margin: 0 });
    s.addText(p, { x: 0.92, y: py, w: 3.7, h: 0.44,
      fontSize: 11, fontFace: "Calibri", color: C.LIGHT, margin: 0, valign: "middle" });
  });

  // Right — solution
  card3d(s, 5.25, 1.0, 4.4, 4.0, { fill: C.CARD2, border: C.BORDER_CYAN, glow: C.CYAN });
  accentBar(s, 5.25, 1.0, 4.0, C.CYAN);

  s.addText("The Solution", { x: 5.45, y: 1.1, w: 4.0, h: 0.35,
    fontSize: 15, fontFace: "Calibri", bold: true, color: C.CYAN, margin: 0 });
  s.addText("AUI Secure", { x: 5.45, y: 1.5, w: 4.0, h: 0.48,
    fontSize: 24, fontFace: "Arial Black", bold: true, color: C.WHITE, margin: 0 });

  const solutions = [
    { t: "Attack in real-time",        c: C.GREEN  },
    { t: "Defend with live code",       c: C.GREEN  },
    { t: "8 hands-on security labs",    c: C.CYAN   },
    { t: "Full OWASP Top 10 coverage",  c: C.CYAN   },
    { t: "Automated 5-stage CI/CD",     c: C.ORANGE },
  ];
  solutions.forEach((sol, i) => {
    const sy = 2.1 + i * 0.58;
    s.addShape(pres.shapes.OVAL, { x: 5.45, y: sy + 0.04, w: 0.28, h: 0.28,
      fill: { color: sol.c }, line: { color: sol.c, width: 0 } });
    s.addText("v", { x: 5.45, y: sy + 0.04, w: 0.28, h: 0.28,
      fontSize: 10, fontFace: "Arial", bold: true, color: C.BG,
      align: "center", valign: "middle", margin: 0 });
    s.addText(sol.t, { x: 5.83, y: sy, w: 3.7, h: 0.44,
      fontSize: 12, fontFace: "Calibri", bold: true, color: C.WHITE,
      margin: 0, valign: "middle" });
  });
}

// ── SLIDE 3 — WHAT IS AUI SECURE? ────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  cornerAccents(s);

  slideTitle(s, "WHAT IS AUI SECURE?");
  titleLine(s, 3.8, C.CYAN);

  s.addText("A dual-layer DevSecOps project: a fully-functional secure web application paired with an automated security CI/CD pipeline.", {
    x: 0.4, y: 0.88, w: 5.5, h: 0.72,
    fontSize: 13, fontFace: "Calibri", color: C.LIGHT, margin: 0
  });

  // Feature cards
  const features = [
    { icon: "🔬", title: "8 Interactive Security Labs",   desc: "SQL Injection, XSS, Password Hashing, CSRF, Rate Limiting, Account Lockout, Security Headers, Audit Trail", color: C.CYAN  },
    { icon: "⚔",  title: "Attack & Defend Side-by-Side", desc: "Every lab has a vulnerable endpoint AND a secure endpoint — see exactly what changes and why it matters",  color: C.RED   },
    { icon: "🛡",  title: "Dark Security Dashboard SPA",  desc: "Zero external JS dependencies, vanilla JS, single CSP nonce-script block, zero npm supply-chain risk",       color: C.GREEN },
  ];
  features.forEach((f, i) => {
    const fy = 1.7 + i * 1.22;
    card3d(s, 0.35, fy, 5.4, 1.1, { fill: C.CARD, border: C.BORDER });
    accentBar(s, 0.35, fy, 1.1, f.color);
    s.addText(f.icon + "  " + f.title, { x: 0.55, y: fy + 0.08, w: 5.1, h: 0.3,
      fontSize: 13, fontFace: "Calibri", bold: true, color: f.color, margin: 0 });
    s.addText(f.desc, { x: 0.55, y: fy + 0.42, w: 5.1, h: 0.55,
      fontSize: 10, fontFace: "Calibri", color: C.LIGHT, margin: 0 });
  });

  // Tech stack panel
  card3d(s, 6.1, 0.86, 3.55, 4.14, { fill: C.CARD2, border: C.BORDER });
  s.addText("TECH STACK", { x: 6.25, y: 0.98, w: 3.2, h: 0.26,
    fontSize: 9, fontFace: "Consolas", bold: true, color: C.GRAY,
    charSpacing: 3, margin: 0 });

  const stack = [
    { name: "Python 3.13 + Flask 3",  color: C.CYAN,   sub: "Web framework + routing"     },
    { name: "SQLite",                  color: C.GREEN,  sub: "Parameterised queries"        },
    { name: "werkzeug scrypt",         color: C.ORANGE, sub: "Memory-hard password hashing" },
    { name: "Flask-Limiter",           color: C.PURPLE, sub: "Rate limiting middleware"     },
    { name: "GitHub Actions",          color: C.CYAN,   sub: "5-stage CI/CD pipeline"       },
    { name: "OWASP ZAP",              color: C.RED,    sub: "DAST scanning"                },
    { name: "Bandit + gitleaks",       color: C.YELLOW, sub: "SAST + secret scanning"       },
    { name: "pip-audit",               color: C.GREEN,  sub: "SCA + auto-remediation"       },
  ];
  stack.forEach((t, i) => {
    const sy = 1.36 + i * 0.44;
    s.addShape(pres.shapes.RECTANGLE, { x: 6.22, y: sy + 0.06, w: 0.06, h: 0.25,
      fill: { color: t.color }, line: { color: t.color, width: 0 } });
    s.addText(t.name, { x: 6.37, y: sy + 0.04, w: 3.1, h: 0.22,
      fontSize: 11, fontFace: "Calibri", bold: true, color: C.WHITE, margin: 0 });
    s.addText(t.sub, { x: 6.37, y: sy + 0.23, w: 3.1, h: 0.17,
      fontSize: 8.5, fontFace: "Calibri", color: C.GRAY, margin: 0 });
  });
}

// ── SLIDE 4 — ARCHITECTURE ────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  cornerAccents(s);

  slideTitle(s, "ARCHITECTURE OVERVIEW");
  titleLine(s, 4.5, C.CYAN);

  // Row 0: Security middleware (green)
  const secBoxes = [
    { label: "CSP Nonce\nHeaders"          },
    { label: "Rate Limiter\nFlask-Limiter" },
    { label: "CSRF Tokens\nSameSite=Lax"  },
    { label: "RBAC\n@requires_role"        },
    { label: "Audit Logger\nlog_action()"  },
  ];
  s.addText("SECURITY LAYER", { x: 0.12, y: 0.84, w: 0.28, h: 1.1,
    fontSize: 7, fontFace: "Consolas", bold: true, color: C.GREEN,
    rotate: 270, align: "center", margin: 0 });

  secBoxes.forEach((b, i) => {
    const bx = 0.52 + i * 1.87;
    card3d(s, bx, 0.84, 1.66, 0.88, { fill: "071A10", border: C.GREEN_DIM });
    s.addText(b.label, { x: bx + 0.08, y: 0.88, w: 1.52, h: 0.78,
      fontSize: 9, fontFace: "Calibri", bold: true, color: C.GREEN,
      align: "center", valign: "middle", margin: 0 });
  });

  // Arrows security→app
  for (let i = 0; i < 5; i++) {
    s.addShape(pres.shapes.LINE, { x: 0.87 + i * 1.87, y: 1.74, w: 0, h: 0.35,
      line: { color: C.GREEN_DIM, width: 1, endArrowType: "open" } });
  }

  // Row 1: Application layer (cyan)
  const appBoxes = [
    { label: "SPA\nindex.html"   },
    { label: "auth.py\nlogin/reg"},
    { label: "lab.py\n8 labs"    },
    { label: "items.py\nCRUD+SQLi"},
    { label: "dashboard\nadmin"  },
  ];
  s.addText("APP LAYER", { x: 0.12, y: 2.08, w: 0.28, h: 1.0,
    fontSize: 7, fontFace: "Consolas", bold: true, color: C.CYAN,
    rotate: 270, align: "center", margin: 0 });

  appBoxes.forEach((b, i) => {
    const bx = 0.52 + i * 1.87;
    card3d(s, bx, 2.1, 1.66, 0.9, { fill: C.CARD3, border: C.BORDER_CYAN });
    s.addText(b.label, { x: bx + 0.08, y: 2.13, w: 1.52, h: 0.83,
      fontSize: 10, fontFace: "Calibri", bold: true, color: C.CYAN,
      align: "center", valign: "middle", margin: 0 });
  });

  // Arrows app→data
  for (let i = 0; i < 5; i++) {
    s.addShape(pres.shapes.LINE, { x: 0.87 + i * 1.87, y: 3.02, w: 0, h: 0.35,
      line: { color: C.BORDER_CYAN, width: 1, endArrowType: "open" } });
  }

  // Row 2: Data layer (orange)
  s.addText("DATA LAYER", { x: 0.12, y: 3.36, w: 0.28, h: 1.0,
    fontSize: 7, fontFace: "Consolas", bold: true, color: C.ORANGE,
    rotate: 270, align: "center", margin: 0 });

  const dataBoxes = [
    { label: "SQLite\nApp DB",       w: 2.2 },
    { label: "audit_logs\ntable",    w: 2.2 },
    { label: "config.py\nenv vars",  w: 2.2 },
    { label: "validators.py\n+bleach", w: 2.15 },
  ];
  let dbx = 0.52;
  dataBoxes.forEach((b) => {
    card3d(s, dbx, 3.38, b.w, 0.85, { fill: "1A1200", border: "3A2A00" });
    s.addText(b.label, { x: dbx + 0.1, y: 3.4, w: b.w - 0.15, h: 0.78,
      fontSize: 10, fontFace: "Calibri", bold: true, color: C.ORANGE,
      align: "center", valign: "middle", margin: 0 });
    dbx += b.w + 0.28;
  });

  // CI/CD bottom bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: 4.38, w: 9.3, h: 0.72,
    fill: { color: "0A0020" }, line: { color: C.PURPLE, width: 1 } });
  s.addText("CI/CD PIPELINE  ->  pytest  ->  gitleaks  ->  Bandit SAST  ->  pip-audit SCA  ->  OWASP ZAP DAST", {
    x: 0.5, y: 4.47, w: 9.0, h: 0.52,
    fontSize: 11, fontFace: "Consolas", bold: true, color: C.PURPLE,
    align: "center", valign: "middle", margin: 0
  });
}

// ── SLIDE 5 — SECURITY LABS ───────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addDotGrid(s);
  cornerAccents(s);

  slideTitle(s, "INTERACTIVE SECURITY LABS");
  s.addText("OWASP Top 10 coverage — attack and defend in real-time", {
    x: 0.5, y: 0.63, w: 9, h: 0.28,
    fontSize: 12, fontFace: "Calibri", color: C.CYAN, align: "center", margin: 0
  });

  const labs = [
    { name: "SQL Injection",     desc: "Fire ' OR 1=1 --\nParam queries vs f-string\nSee live SQL generated",    icon: "💉", color: C.RED    },
    { name: "XSS",               desc: "<script>alert()</script>\nbleach + html.escape()\nCSP nonce allowlist",   icon: "⚡", color: C.RED    },
    { name: "Password Hashing",  desc: "scrypt salted hashes\nSame input, diff hash\nStrength meter live",        icon: "🔐", color: C.ORANGE },
    { name: "Security Headers",  desc: "7 HTTP headers shown\nCSP, HSTS, X-Frame-Options\nSeverity ratings",     icon: "🛡", color: C.GREEN  },
    { name: "CSRF Protection",   desc: "Forged form demo\nSameSite=Lax cookies\nTiming-safe token compare",       icon: "🎭", color: C.PURPLE },
    { name: "Rate Limiting",     desc: "Hammer the endpoint\n200 -> 429 responses\nLive counter on screen",       icon: "⏱", color: C.CYAN   },
    { name: "Account Lockout",   desc: "Brute-force demo\nExponential backoff\nMax 24h lockout shown",            icon: "🔒", color: C.YELLOW },
    { name: "Audit Trail",       desc: "Every action logged\nIP, user, timestamp\nAuto-refresh live feed",        icon: "📋", color: C.GREEN  },
  ];

  const cw = 2.18, ch = 1.84;
  const startX = 0.35, startY = 0.98;

  labs.forEach((lab, i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    const lx = startX + col * (cw + 0.14);
    const ly = startY + row * (ch + 0.15);

    card3d(s, lx, ly, cw, ch, { fill: C.CARD, border: C.BORDER });

    // Top stripe
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: ly, w: cw, h: 0.08,
      fill: { color: lab.color }, line: { color: lab.color, width: 0 } });

    // Icon
    s.addText(lab.icon, { x: lx + 0.12, y: ly + 0.14, w: 0.5, h: 0.44,
      fontSize: 22, margin: 0 });

    // Name
    s.addText(lab.name, { x: lx + 0.65, y: ly + 0.16, w: cw - 0.75, h: 0.44,
      fontSize: 12, fontFace: "Calibri", bold: true, color: lab.color, margin: 0 });

    // Description
    s.addText(lab.desc, { x: lx + 0.14, y: ly + 0.66, w: cw - 0.24, h: 1.06,
      fontSize: 9.5, fontFace: "Calibri", color: C.LIGHT, margin: 0 });
  });
}

// ── SLIDE 6 — SECURITY MECHANISMS ────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  cornerAccents(s);

  slideTitle(s, "SECURITY MECHANISMS DEEP DIVE");
  titleLine(s, 5.5, C.GREEN);

  const mechs = [
    { cat: "Authentication",   color: C.CYAN,   items: ["werkzeug scrypt — memory-hard hashing", "Session rotation on every login", "HttpOnly + SameSite=Lax cookies", "Configurable session lifetime"] },
    { cat: "RBAC",            color: C.PURPLE, items: ["@requires_auth decorator", "@requires_role('admin') decorator", "User and Admin role system", "API key Bearer token auth"] },
    { cat: "Account Lockout", color: C.ORANGE, items: ["Exponential backoff: base x 2^n", "Max lockout duration: 24 hours", "Progressive delay up to 5s/attempt", "Per-user state stored in DB"] },
    { cat: "Input Validation", color: C.GREEN,  items: ["Username + password regex policy", "bleach HTML tag stripping", "html.escape() entity encoding", "Null-byte removal"] },
    { cat: "SQL Injection",   color: C.RED,    items: ["Parameterised queries everywhere", "db.execute(sql, (param,)) pattern", "Dual endpoints for live comparison", "Zero f-string SQL anywhere"] },
    { cat: "XSS Defence",     color: C.RED,    items: ["bleach strips all HTML tags", "html.escape() encodes all entities", "CSP nonce-based script allowlist", "Zero inline event handlers"] },
  ];

  const bw = 3.0, bh = 1.62;
  const sx = 0.35, sy = 0.84;

  mechs.forEach((m, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const mx = sx + col * (bw + 0.22);
    const my = sy + row * (bh + 0.16);

    card3d(s, mx, my, bw, bh, { fill: C.CARD, border: C.BORDER });
    accentBar(s, mx, my, bh, m.color);

    s.addText(m.cat, { x: mx + 0.18, y: my + 0.1, w: bw - 0.25, h: 0.3,
      fontSize: 12, fontFace: "Calibri", bold: true, color: m.color, margin: 0 });

    m.items.forEach((item, j) => {
      s.addShape(pres.shapes.OVAL, { x: mx + 0.2, y: my + 0.5 + j * 0.26 + 0.04, w: 0.1, h: 0.1,
        fill: { color: m.color }, line: { color: m.color, width: 0 } });
      s.addText(item, { x: mx + 0.38, y: my + 0.5 + j * 0.26, w: bw - 0.46, h: 0.25,
        fontSize: 9.5, fontFace: "Calibri", color: C.LIGHT, margin: 0 });
    });
  });
}

// ── SLIDE 7 — CI/CD PIPELINE ──────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addDotGrid(s);
  cornerAccents(s);

  slideTitle(s, "CI/CD SECURITY PIPELINE — 5-STAGE GAUNTLET");
  s.addText("Every git push triggers automated security checks — zero manual intervention required", {
    x: 0.5, y: 0.66, w: 9, h: 0.28,
    fontSize: 12, fontFace: "Calibri", color: C.CYAN, align: "center", margin: 0
  });

  const stages = [
    { n: "01", name: "Build &\nTests",    tool: "pytest",         sub: "Unit + security\ntest suite",   color: C.GREEN  },
    { n: "02", name: "Secret\nScanning",  tool: "gitleaks",       sub: "Blocks hardcoded\nsecrets",     color: C.RED    },
    { n: "03", name: "SAST",             tool: "Bandit",         sub: "Static code\nsecurity analysis", color: C.ORANGE },
    { n: "04", name: "SCA +\nAuto-Fix",  tool: "pip-audit +\nremediate.py", sub: "Opens PR on\nvuln deps", color: C.PURPLE },
    { n: "05", name: "DAST",            tool: "OWASP ZAP",      sub: "Live app scan\nbaseline check",  color: C.CYAN   },
  ];

  const sw = 1.72, stH = 2.65;
  const stY = 1.05;
  const gap = 0.11;
  const totalW = stages.length * sw + (stages.length - 1) * gap;
  const stX = (W - totalW) / 2;

  stages.forEach((st, i) => {
    const bx = stX + i * (sw + gap);

    card3d(s, bx, stY, sw, stH, { fill: C.CARD2, border: C.BORDER });

    // Color top band
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: stY, w: sw, h: 0.32,
      fill: { color: st.color }, line: { color: st.color, width: 0 } });

    // Stage number
    s.addText(st.n, { x: bx, y: stY, w: sw, h: 0.32,
      fontSize: 13, fontFace: "Consolas", bold: true, color: C.BG,
      align: "center", valign: "middle", margin: 0 });

    // Name
    s.addText(st.name, { x: bx + 0.1, y: stY + 0.37, w: sw - 0.2, h: 0.7,
      fontSize: 13, fontFace: "Calibri", bold: true, color: C.WHITE,
      align: "center", valign: "middle", margin: 0 });

    // Tool badge
    s.addShape(pres.shapes.RECTANGLE, { x: bx + 0.14, y: stY + 1.14, w: sw - 0.28, h: 0.42,
      fill: { color: "0C1420" }, line: { color: st.color, width: 1 } });
    s.addText(st.tool, { x: bx + 0.14, y: stY + 1.14, w: sw - 0.28, h: 0.42,
      fontSize: 9, fontFace: "Consolas", bold: true, color: st.color,
      align: "center", valign: "middle", margin: 0 });

    // Sub
    s.addText(st.sub, { x: bx + 0.1, y: stY + 1.65, w: sw - 0.2, h: 0.88,
      fontSize: 9, fontFace: "Calibri", color: C.LIGHT,
      align: "center", margin: 0 });

    // Arrow to next
    if (i < stages.length - 1) {
      s.addShape(pres.shapes.LINE, { x: bx + sw + 0.01, y: stY + stH / 2, w: gap + 0.02, h: 0,
        line: { color: C.CYAN_DIM, width: 1.5, endArrowType: "open" } });
    }
  });

  // Auto-remediation callout
  card3d(s, 1.8, 3.88, 6.4, 0.7, { fill: "0A0020", border: C.PURPLE, glow: C.PURPLE });
  s.addText("AUTO-REMEDIATION:", { x: 2.0, y: 3.94, w: 2.4, h: 0.28,
    fontSize: 11, fontFace: "Consolas", bold: true, color: C.PURPLE, margin: 0 });
  s.addText("pip-audit finds vuln deps  ->  remediate.py patches requirements.txt  ->  opens GitHub PR automatically", {
    x: 4.5, y: 3.94, w: 3.5, h: 0.5,
    fontSize: 9, fontFace: "Calibri", color: C.LIGHT, margin: 0 });
}

// ── SLIDE 8 — PRE-COMMIT HOOKS ────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  cornerAccents(s);

  slideTitle(s, "PRE-COMMIT HOOKS — SHIFT LEFT");
  titleLine(s, 5.0, C.GREEN);

  s.addText("Same checks as CI/CD — caught at the developer's workstation before anything reaches GitHub", {
    x: 0.5, y: 0.7, w: 9, h: 0.26,
    fontSize: 11, fontFace: "Calibri", color: C.LIGHT, margin: 0
  });

  const hooks = [
    { tool: "black",     cat: "Code Formatting",  desc: "Enforces consistent code style. Fails the commit if formatting is off — fixes applied automatically.", color: C.CYAN   },
    { tool: "bandit",    cat: "SAST",             desc: "Static security analysis. Flags dangerous patterns: shell injection, hardcoded secrets, insecure hash algorithms.", color: C.RED    },
    { tool: "pip-audit", cat: "SCA",              desc: "Scans all dependencies against NVD CVE database. Blocks commits with known-vulnerable packages.", color: C.ORANGE },
    { tool: "gitleaks",  cat: "Secret Detection", desc: "Scans git history and staged changes for API keys, tokens, passwords. Blocks before they leave the machine.", color: C.PURPLE },
    { tool: "hygiene",   cat: "File Hygiene",     desc: "Checks YAML/JSON validity, merge conflict markers, private key file detection, large binary files.", color: C.GREEN  },
  ];

  hooks.forEach((h, i) => {
    const hy = 1.08 + i * 0.84;
    card3d(s, 0.35, hy, 9.3, 0.74, { fill: C.CARD, border: C.BORDER });
    accentBar(s, 0.35, hy, 0.74, h.color);

    // Tool badge
    s.addShape(pres.shapes.RECTANGLE, { x: 0.55, y: hy + 0.15, w: 1.18, h: 0.38,
      fill: { color: h.color }, line: { color: h.color, width: 0 } });
    s.addText(h.tool, { x: 0.55, y: hy + 0.15, w: 1.18, h: 0.38,
      fontSize: 12, fontFace: "Consolas", bold: true, color: C.BG,
      align: "center", valign: "middle", margin: 0 });

    s.addText(h.cat, { x: 1.85, y: hy + 0.08, w: 2.0, h: 0.26,
      fontSize: 9, fontFace: "Consolas", bold: true, color: h.color, margin: 0 });
    s.addText(h.desc, { x: 1.85, y: hy + 0.36, w: 7.65, h: 0.3,
      fontSize: 10, fontFace: "Calibri", color: C.LIGHT, margin: 0 });
  });

  // Success line
  s.addText("$ git commit  ->  black ok  ->  bandit ok  ->  pip-audit ok  ->  gitleaks ok  ->  All checks passed.", {
    x: 0.35, y: 5.28, w: 9.3, h: 0.26,
    fontSize: 9, fontFace: "Consolas", color: C.GREEN, margin: 0
  });
}

// ── SLIDE 9 — OWASP TOP 10 ────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  cornerAccents(s);

  slideTitle(s, "OWASP TOP 10 COVERAGE");
  titleLine(s, 4.5, C.RED);

  const owasp = [
    { id: "A01", name: "Broken Access Control",       mit: "RBAC + @requires_role",           color: C.RED    },
    { id: "A02", name: "Cryptographic Failures",      mit: "scrypt, HttpOnly cookies",        color: C.ORANGE },
    { id: "A03", name: "Injection (SQL Injection)",   mit: "Parameterised queries",            color: C.RED    },
    { id: "A04", name: "Insecure Design",             mit: "SECURE_MODE gating",               color: C.YELLOW },
    { id: "A05", name: "Security Misconfiguration",   mit: "Security headers, CSP nonce",     color: C.ORANGE },
    { id: "A06", name: "Vulnerable Components",       mit: "pip-audit + auto-remediation",    color: C.PURPLE },
    { id: "A07", name: "Auth & Session Failures",     mit: "Lockout, session rotation",       color: C.RED    },
    { id: "A08", name: "Software Integrity Failures", mit: "gitleaks, secret scanning",       color: C.CYAN   },
    { id: "A09", name: "Logging & Monitoring Gaps",   mit: "Audit trail, live event feed",    color: C.GREEN  },
    { id: "A10", name: "Server-Side Request Forgery", mit: "No outbound requests made",       color: C.GREEN  },
  ];

  const colW = 4.5, rh = 0.44;
  const sy = 0.78;

  owasp.forEach((item, i) => {
    const col = i < 5 ? 0 : 1;
    const row = i < 5 ? i : i - 5;
    const ox = 0.35 + col * (colW + 0.3);
    const oy = sy + row * (rh + 0.05);

    s.addShape(pres.shapes.RECTANGLE, { x: ox, y: oy, w: colW, h: rh,
      fill: { color: row % 2 === 0 ? C.CARD : "0C1520" },
      line: { color: C.BORDER, width: 0.5 } });

    // ID badge
    s.addShape(pres.shapes.RECTANGLE, { x: ox, y: oy, w: 0.62, h: rh,
      fill: { color: item.color }, line: { color: item.color, width: 0 } });
    s.addText(item.id, { x: ox, y: oy, w: 0.62, h: rh,
      fontSize: 9.5, fontFace: "Consolas", bold: true, color: C.BG,
      align: "center", valign: "middle", margin: 0 });

    s.addText(item.name, { x: ox + 0.7, y: oy + 0.03, w: 1.9, h: rh - 0.06,
      fontSize: 9.5, fontFace: "Calibri", bold: true, color: C.WHITE,
      margin: 0, valign: "middle" });

    s.addText("->  " + item.mit, { x: ox + 2.65, y: oy + 0.03, w: 1.74, h: rh - 0.06,
      fontSize: 9, fontFace: "Calibri", color: C.GREEN, margin: 0, valign: "middle" });

    s.addText("OK", { x: ox + colW - 0.38, y: oy + 0.03, w: 0.34, h: rh - 0.06,
      fontSize: 11, fontFace: "Calibri", bold: true, color: C.GREEN,
      align: "center", valign: "middle", margin: 0 });
  });

  // Summary
  card3d(s, 2.5, 5.2, 5.0, 0.34, { fill: C.CARD2, border: C.GREEN_DIM, glow: C.GREEN });
  s.addText("10 / 10  OWASP TOP 10 VULNERABILITIES — DEMONSTRATED + MITIGATED", {
    x: 2.5, y: 5.2, w: 5.0, h: 0.34,
    fontSize: 10.5, fontFace: "Consolas", bold: true, color: C.GREEN,
    align: "center", valign: "middle", margin: 0
  });
}

// ── SLIDE 10 — DESIGN DECISIONS ───────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  cornerAccents(s);

  slideTitle(s, "KEY DESIGN DECISIONS");
  titleLine(s, 4.0, C.CYAN);

  const decisions = [
    { q: "Why SECURE_MODE toggle?", icon: "🔀",
      a: "Insecure endpoints intentionally included for education — guarded by server-side env flag. Default is SECURE_MODE=true (safe). Set false for demos only. Security is configurable, not removed.",
      color: C.CYAN },
    { q: "Why no frontend framework?", icon: "🌐",
      a: "Zero external JS dependencies = zero npm supply-chain risk. Entire SPA is vanilla JS in one <script nonce='...'> block. This makes the CSP policy trivially correct and auditable.",
      color: C.GREEN },
    { q: "Why scrypt over bcrypt?", icon: "🔑",
      a: "werkzeug 3.x defaults to scrypt — memory-hard, resists GPU-based attacks better than bcrypt. Algorithm upgrades are transparent via werkzeug's API. No migration needed.",
      color: C.ORANGE },
    { q: "Why SQLite?", icon: "🗄",
      a: "Simplicity for demonstration. All parameterised query patterns are identical to PostgreSQL and MySQL. The security lesson is database-agnostic and the patterns transfer directly.",
      color: C.PURPLE },
  ];

  const dw = 4.55, dh = 1.95;
  const positions = [
    { x: 0.35, y: 0.84 }, { x: 5.1,  y: 0.84 },
    { x: 0.35, y: 2.9  }, { x: 5.1,  y: 2.9  },
  ];

  decisions.forEach((d, i) => {
    const { x, y } = positions[i];
    card3d(s, x, y, dw, dh, { fill: C.CARD, border: C.BORDER });

    // Top colour stripe
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: dw, h: 0.06,
      fill: { color: d.color }, line: { color: d.color, width: 0 } });

    s.addText(d.icon, { x: x + 0.15, y: y + 0.14, w: 0.45, h: 0.45, fontSize: 22, margin: 0 });
    s.addText(d.q, { x: x + 0.65, y: y + 0.14, w: dw - 0.75, h: 0.45,
      fontSize: 13, fontFace: "Calibri", bold: true, color: d.color, margin: 0 });
    s.addText(d.a, { x: x + 0.2, y: y + 0.68, w: dw - 0.35, h: 1.14,
      fontSize: 10.5, fontFace: "Calibri", color: C.LIGHT, margin: 0 });
  });
}

// ── SLIDE 11 — LIVE DEMO ──────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addDotGrid(s);
  cornerAccents(s);

  slideTitle(s, "LIVE DEMO GUIDE");
  titleLine(s, 3.5, C.CYAN);

  // Start command
  card3d(s, 0.35, 0.8, 9.3, 0.5, { fill: "060E1A", border: "0A3050" });
  s.addText("$ set SECURE_MODE=false && python run.py     ->     http://localhost:5000", {
    x: 0.55, y: 0.85, w: 9.0, h: 0.36,
    fontSize: 11, fontFace: "Consolas", bold: true, color: C.GREEN, margin: 0
  });

  const steps = [
    { n: "1", title: "SQL Injection",     icon: "💉",
      vuln: "Attack:  ' OR '1'='1  ->  all rows returned (f-string SQL, no escaping)",
      def:  "Defend:  Same payload, zero results — parameterised query db.execute(sql, (q,)) blocks it",
      color: C.RED },
    { n: "2", title: "XSS",              icon: "⚡",
      vuln: "Attack:  <script>alert('XSS')</script>  ->  raw HTML reflected in response",
      def:  "Defend:  Tags stripped by bleach, entities escaped by html.escape(), CSP blocks execution",
      color: C.RED },
    { n: "3", title: "Password Hashing", icon: "🔐",
      vuln: "Enter same password twice  ->  completely different scrypt hashes each time",
      def:  "Both verify as true — random salt per hash defeats rainbow tables completely",
      color: C.ORANGE },
    { n: "4", title: "Rate Limiting",    icon: "⏱",
      vuln: "Rapid-fire requests  ->  HTTP 200 responses flip to HTTP 429 Too Many Requests",
      def:  "Live counter shows exactly when limit trips — Flask-Limiter per-IP enforcement",
      color: C.CYAN },
    { n: "5", title: "Audit Trail",      icon: "📋",
      vuln: "Every action logged: SQL queries, XSS attempts, login failures, API calls",
      def:  "Visible in live events feed with IP, user, timestamp, success/fail — auto-refreshes",
      color: C.GREEN },
  ];

  steps.forEach((st, i) => {
    const sy = 1.4 + i * 0.82;
    card3d(s, 0.35, sy, 9.3, 0.73, { fill: C.CARD, border: C.BORDER });

    // Number
    s.addShape(pres.shapes.OVAL, { x: 0.44, y: sy + 0.2, w: 0.34, h: 0.34,
      fill: { color: st.color }, line: { color: st.color, width: 0 } });
    s.addText(st.n, { x: 0.44, y: sy + 0.2, w: 0.34, h: 0.34,
      fontSize: 11, fontFace: "Arial", bold: true, color: C.BG,
      align: "center", valign: "middle", margin: 0 });

    s.addText(st.icon + "  " + st.title, { x: 0.88, y: sy + 0.07, w: 2.1, h: 0.3,
      fontSize: 12, fontFace: "Calibri", bold: true, color: st.color, margin: 0 });
    s.addText("> " + st.vuln, { x: 0.88, y: sy + 0.37, w: 8.55, h: 0.18,
      fontSize: 9, fontFace: "Consolas", color: C.RED, margin: 0 });
    s.addText("+ " + st.def, { x: 0.88, y: sy + 0.54, w: 8.55, h: 0.18,
      fontSize: 9, fontFace: "Consolas", color: C.GREEN, margin: 0 });
  });
}

// ── SLIDE 12 — CONCLUSION ─────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.BG };
  addGridLines(s);
  addDotGrid(s);
  cornerAccents(s);

  // Glow backdrop
  s.addShape(pres.shapes.OVAL, { x: 1.5, y: 0.45, w: 7, h: 3.5,
    fill: { color: "00162A", transparency: 20 }, line: { color: "00162A", width: 0 } });

  // Quote
  s.addText('"Security is not a feature you bolt on at the end —', {
    x: 0.5, y: 0.3, w: 9, h: 0.44,
    fontSize: 17, fontFace: "Calibri", italic: true, color: C.CYAN,
    align: "center", margin: 0
  });
  s.addText("it's an architectural concern threaded through every layer.\"", {
    x: 0.5, y: 0.73, w: 9, h: 0.44,
    fontSize: 17, fontFace: "Calibri", italic: true, color: C.CYAN,
    align: "center", margin: 0
  });

  // Three takeaway cards
  const takeaways = [
    { icon: "🏗",  title: "Design Phase",  body: "Threat modelling\nSECURE_MODE toggle\nRBAC schema design",       color: C.CYAN   },
    { icon: "🔬", title: "Code + Test",   body: "Parameterised queries\nCSP nonce pattern\nSecurity pytest suite",   color: C.GREEN  },
    { icon: "⚙",  title: "CI/CD Phase",   body: "SAST · SCA · DAST\nAuto-remediation\nPre-commit hooks",            color: C.ORANGE },
  ];

  const cw = 2.9, ch = 2.05;
  takeaways.forEach((c, i) => {
    const cx = 0.55 + i * (cw + 0.35);
    card3d(s, cx, 1.35, cw, ch, { fill: C.CARD2, border: C.BORDER, glow: c.color });

    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 1.35, w: cw, h: 0.09,
      fill: { color: c.color }, line: { color: c.color, width: 0 } });

    s.addText(c.icon, { x: cx + 0.15, y: 1.5, w: 0.55, h: 0.55, fontSize: 26, margin: 0 });
    s.addText(c.title, { x: cx + 0.75, y: 1.53, w: cw - 0.85, h: 0.44,
      fontSize: 14, fontFace: "Calibri", bold: true, color: c.color, margin: 0 });
    s.addText(c.body, { x: cx + 0.18, y: 2.06, w: cw - 0.3, h: 1.22,
      fontSize: 11, fontFace: "Calibri", color: C.LIGHT, margin: 0 });
  });

  // Stats row
  const stats = [
    { n: "8",     label: "Interactive Labs"  },
    { n: "10/10", label: "OWASP Coverage"   },
    { n: "5",     label: "Pipeline Stages"  },
    { n: "100%",  label: "Tests Passing"    },
  ];
  stats.forEach((st, i) => {
    const stx = 0.55 + i * 2.3;
    s.addText(st.n, { x: stx, y: 3.6, w: 2.1, h: 0.56,
      fontSize: 30, fontFace: "Arial Black", bold: true, color: C.WHITE,
      align: "center", margin: 0 });
    s.addText(st.label, { x: stx, y: 4.18, w: 2.1, h: 0.26,
      fontSize: 10, fontFace: "Calibri", color: C.GRAY,
      align: "center", margin: 0 });
  });

  s.addShape(pres.shapes.LINE, { x: 0.5, y: 4.5, w: 9, h: 0,
    line: { color: C.BORDER, width: 0.75 } });

  s.addText("AUI Secure  ·  Secure Software Design with Secure Coding Implementation  ·  2026", {
    x: 0.5, y: 4.6, w: 9, h: 0.27,
    fontSize: 9, fontFace: "Calibri", color: C.GRAY, align: "center", margin: 0
  });
  s.addText("github.com/your-username/CdPipeline", {
    x: 0.5, y: 4.9, w: 9, h: 0.26,
    fontSize: 10, fontFace: "Consolas", color: C.CYAN, align: "center", margin: 0
  });
}

// ── WRITE ─────────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "C:/Users/dumbutthehe/Desktop/CdPipeline/AUI_Secure_Presentation.pptx" })
  .then(() => console.log("Saved: AUI_Secure_Presentation.pptx"))
  .catch(e => { console.error("ERROR:", e); process.exit(1); });

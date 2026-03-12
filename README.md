# 🔐 Secure DevSecOps CI/CD Pipeline Implementation

> A university course project demonstrating enterprise-grade DevSecOps practices — shifting security left into every stage of the software development lifecycle.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Team](#-team)
- [Architecture](#-architecture)
- [Tech Stack & Security Tools](#-tech-stack--security-tools)
- [Security Policies](#-security-policies)
- [Project Phases](#-project-phases)
- [Threat Model (STRIDE)](#-threat-model-stride)
- [Risk Register](#-risk-register)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Getting Started](#-getting-started)
- [Documentation](#-documentation)

---

## 🌐 Project Overview

This project implements a **DevSecOps CI/CD Pipeline** for a web application, integrating automated security scanning directly into the development and deployment workflow. The goal is to demonstrate the **"shift left"** security philosophy — catching vulnerabilities early in development rather than after deployment.

### Key Objectives

- Build a web application with realistic (intentional) security vulnerabilities for testing
- Automate Static Application Security Testing (SAST) and Software Composition Analysis (SCA) via CI/CD
- Enforce security gates that block insecure code from merging
- Align implementation with **OWASP Top 10 (2021)**, **NIST SSDF**, and **DSOMM Level 2**

### Course & Supervisor

| Field | Details |
|-------|---------|
| **Course** | Secure Software Development |
| **Instructor** | Dr. Zubair Ahmad |

---

## 👥 Team

| Name | Student ID | Responsibility |
|------|-----------|---------------|
| Muhammad Abubakar | 2023352 | Application Development (Phase 2) |
| Muhammad Ismail | 2023453 | Pipeline Configuration (Phase 3) |
| Usman Ali | 2023581 | Testing & Validation (Phase 4) |
| All Members | — | Planning, Documentation & Demo (Phases 1 & 5) |

---

## 🏗️ Architecture

The system is organized into three security zones:

```
┌─────────────────────────────────────────────────────────────────────┐
│                       SYSTEM ARCHITECTURE                           │
├──────────────────┬──────────────────────┬───────────────────────────┤
│  LAYER 1         │  LAYER 2             │  LAYER 3                  │
│  Developer       │  GitHub / CI-CD      │  Deployed Application     │
│  Workstation     │  Pipeline            │                           │
│  (Untrusted)     │  (Semi-Trusted)      │  (Trusted)                │
│                  │                      │                           │
│  • Git / IDE     │  • GitHub Repo       │  • Flask / Express App    │
│  • Local Tests   │  • GitHub Actions    │  • Database (SQLite/PG)   │
│                  │  • Bandit (SAST)     │  • End User Browser       │
│                  │  • pip-audit / npm   │                           │
│                  │    audit (SCA)       │                           │
│                  │  • GitHub Secrets    │                           │
└──────────────────┴──────────────────────┴───────────────────────────┘
```

### Data Flows

1. **Developer → GitHub Repo**: Code push / pull request
2. **GitHub Repo → GitHub Actions**: CI trigger on push/PR
3. **GitHub Actions → Security Tools**: SAST & SCA scan execution
4. **GitHub Actions → Deployed App**: Deploy artifact (on passing gates)

---

## 🛠️ Tech Stack & Security Tools

### Application

| Component | Technology |
|-----------|-----------|
| Language & Framework | Python 3 + Flask **or** Node.js + Express |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Authentication | Session-based / Token-based; bcrypt (cost ≥ 12) |

### Security Tools

| Tool | Category | Purpose |
|------|----------|---------|
| **Bandit** | SAST (Python) | Detects insecure function calls and hardcoded secrets in Python source |
| **pip-audit** | SCA (Python) | Scans Python dependencies for known CVEs |
| **npm audit** | SCA (Node.js) | Scans npm packages for known vulnerabilities |
| **GitHub Secrets** | Secrets Management | Encrypted storage for credentials and API keys |
| **Branch Protection** | Process Control | Enforces code review and passing status checks before merge |

### CI/CD Platform

| Component | Technology |
|-----------|-----------|
| Pipeline | GitHub Actions (YAML workflows) |
| Version Control | GitHub |
| Secret Storage | GitHub Encrypted Secrets |

### Compliance Frameworks

| Framework | Role |
|-----------|------|
| **OWASP Top 10 (2021)** | Security requirement basis |
| **NIST SSDF** | Project phase alignment |
| **DSOMM Level 2** | Target maturity: automated security testing with policy-enforced gates |
| **STRIDE** | Threat modeling methodology |
| **ISO 31000 / NIST SP 800-30** | Risk management approach |

---

## 🔒 Security Policies

### Core Policies

| ID | Policy | Description |
|----|--------|-------------|
| **P-01** | Zero High-Risk Code | Build fails immediately on any High or Critical severity SAST finding |
| **P-02** | Secrets Management | No hardcoded credentials; all secrets stored in GitHub Secrets |
| **P-03** | Dependency Vetting | All third-party libraries scanned on every commit; Critical CVEs block merge |
| **P-04** | Least Privilege | Every pipeline step and application component has minimum required permissions |
| **P-05** | Audit Logging | All pipeline runs, security scan results, and deployments are logged and retained |
| **P-06** | Code Review | No direct pushes to `main`; all changes require a reviewed and approved pull request |

### Security Requirements Summary

| Category | ID Prefix | Count | Examples |
|----------|-----------|-------|---------|
| Authentication & Authorization | SR-AUTH | 6 | MFA-ready, bcrypt hashing, session expiry |
| Input Validation & Output Encoding | SR-INP | 4 | Allowlist validation, parameterized queries, XSS prevention |
| Data Protection | SR-DAT | 4 | TLS 1.2+, AES-256 at rest, secrets masking |
| Error Handling & Logging | SR-ERR | 3 | Generic user errors, detailed server-side logs, no secrets in logs |

### Non-Functional Requirements (NFRs)

- Pipeline completes in **< 10 minutes**
- SAST false-positive rate **< 15%**
- **100%** of source files covered by SAST scan
- Dependency scan runs on **every commit** and **every pull request**
- All High/Critical findings trigger **automatic build failure**

---

## 📅 Project Phases

| Phase | Activity | Lead | Status |
|-------|----------|------|--------|
| **1** | Security Requirements, Risk Register & Threat Modeling | All Members | ✅ Complete |
| **2** | Vulnerable Web Application Development | Abubakar (2023352) | 🔲 Pending |
| **3** | GitHub Actions CI/CD Pipeline Configuration | Ismail (2023453) | 🔲 Pending |
| **4** | Testing, Validation & Evidence Collection | Usman (2023581) | 🔲 Pending |
| **5** | Final Report, Demo & Documentation | All Members | 🔲 Pending |

---

## ⚠️ Threat Model (STRIDE)

The following STRIDE threats were analyzed across all nine system components:

| Threat | Example | Mitigation |
|--------|---------|-----------|
| **S**poofing | Stolen credentials, account impersonation | MFA readiness, secure session tokens |
| **T**ampering | SQL injection, XSS, code modification | Parameterized queries, output encoding, signed commits |
| **R**epudiation | Denying unauthorized actions | Audit logging for all pipeline events and user actions |
| **I**nformation Disclosure | Secrets/passwords in logs or error messages | GitHub Secrets, generic error messages, log sanitization |
| **D**enial of Service | Login endpoint flooding, pipeline outages | Rate limiting, GitHub Actions redundancy |
| **E**levation of Privilege | IDOR attacks, workflow abuse, privilege escalation | Server-side authorization, branch protection, least privilege |

> Full threat model: [`D1_Threat_Modeling.pdf`](D1_Threat_Modeling.pdf)

---

## 📊 Risk Register

### Application Security Risks

| ID | Risk | Likelihood | Impact | Score | Treatment |
|----|------|-----------|--------|-------|-----------|
| R-APP-01 | Hardcoded secrets | High | Critical | 20 | Bandit scan + GitHub Secrets |
| R-APP-02 | SQL Injection | High | High | 15 | Parameterized queries + SAST gate |
| R-APP-03 | XSS vulnerabilities | High | High | 12 | Output encoding + CSP headers |
| R-APP-04 | Broken Authentication | Medium | High | 10 | bcrypt + session expiry |
| R-APP-05 | IDOR vulnerabilities | Medium | Medium | 8 | Server-side authorization checks |

### Dependency & Supply Chain Risks

| ID | Risk | Score | Treatment |
|----|------|-------|-----------|
| R-DEP-01 | Known CVEs in libraries | 15 | pip-audit / npm audit gates |
| R-DEP-02 | Dependency confusion | 5 | Pinned versions + hash verification |
| R-DEP-03 | Outdated dependencies | 9 | Automated dependency update checks |

### CI/CD Pipeline Risks

| ID | Risk | Score | Treatment |
|----|------|-------|-----------|
| R-PIPE-01 | Secrets exposed in build logs | 15 | GitHub Secrets masking |
| R-PIPE-02 | Pipeline misconfiguration | 10 | Peer review of workflow YAML |
| R-PIPE-03 | Malicious code injection | 5 | Branch protection + signed commits |
| R-PIPE-04 | GitHub Actions outage | 4 | Accept — monitored via status page |

> Full risk register: [`D1_Risk_Management.pdf`](D1_Risk_Management.pdf)

---

## ⚙️ CI/CD Pipeline

> **Note**: Pipeline implementation is in progress (Phase 3). The diagram below reflects the planned workflow.

```
Developer Push / Pull Request
         │
         ▼
┌─────────────────────┐
│   GitHub Actions    │
│   Workflow Trigger  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Dependency Scan    │  ← pip-audit / npm audit
│  (SCA)              │    Fail on Critical CVEs
└─────────┬───────────┘
          │ PASS
          ▼
┌─────────────────────┐
│  Static Analysis    │  ← Bandit (Python SAST)
│  (SAST)             │    Fail on High/Critical findings
└─────────┬───────────┘
          │ PASS
          ▼
┌─────────────────────┐
│  Build & Test       │  ← Unit tests, integration tests
└─────────┬───────────┘
          │ PASS
          ▼
┌─────────────────────┐
│  Deploy             │  ← Only after all gates pass
│  (Gated)            │
└─────────────────────┘
```

### Security Gates

- ❌ **BLOCK**: Any High or Critical SAST finding → build fails, merge blocked
- ❌ **BLOCK**: Any Critical CVE in dependencies → build fails, merge blocked
- ✅ **PASS**: All findings resolved or accepted with documented justification

---

## 🚀 Getting Started

> **Note**: Application code and pipeline configuration are being developed in Phases 2–3. Instructions will be updated as implementation progresses.

### Prerequisites (Planned)

```bash
# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install security tools locally
pip install bandit pip-audit
```

### Running the Application (Planned)

```bash
# Start the Flask development server
python app.py
```

### Running Security Scans Locally (Planned)

```bash
# SAST — Python static analysis
bandit -r . -ll

# SCA — Python dependency vulnerability scan
pip-audit

# SCA — Node.js dependency vulnerability scan
npm audit
```

---

## 📁 Documentation

| Document | Description |
|----------|-------------|
| [`project proposal.pdf`](project%20proposal.pdf) | Project proposal, goals, and team assignment |
| [`D1_Security_Requirements_Planning.pdf`](D1_Security_Requirements_Planning.pdf) | Full security requirements specification (36+ requirements, traceability matrix) |
| [`D1_Threat_Modeling.pdf`](D1_Threat_Modeling.pdf) | STRIDE threat model across all system components |
| [`D1_Risk_Management.pdf`](D1_Risk_Management.pdf) | Risk register, heat map, and treatment strategies (ISO 31000 / NIST SP 800-30) |

---

## 📜 License

This project is produced for academic purposes as part of a university course on Secure Software Development.

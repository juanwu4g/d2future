# d2future — Company Homepage

A single-page homepage for **d2future**, a Tokyo-based forward-deployed engineering
firm (AI Agents, Cloud Native, Data Engineering), shipped as **one Docker container**.

It serves a static frontend plus a tiny FastAPI backend: a health check and a contact
endpoint that logs submissions to stdout (no email, no database).

---

## Quick start

```bash
docker build -t d2future-homepage .
docker run --rm -p 8080:8080 d2future-homepage
```

Then open **http://localhost:8080**.

- Health check: `GET http://localhost:8080/health` → `{"status":"ok"}`
- Contact form posts to `POST /api/contact`; submissions appear in the container's
  stdout (`docker logs`).

> **Port:** the app listens on **8080** (HTTP). Change it in `Dockerfile` (the `EXPOSE`
> + `CMD`) and the `-p` flag above if needed.

---

## Stack choice & rationale

**Python 3.12 + FastAPI + Uvicorn, serving a vanilla HTML/CSS/JS frontend.**

I chose FastAPI because it gives typed, auto-validated endpoints with almost no
boilerplate — the contact payload is a Pydantic model, so malformed input returns a
`422` for free, which is a clean correctness signal. The frontend is plain HTML/CSS/JS
with **no build step**, so there is no `node_modules` and nothing to go stale. The image
is a **multi-stage build** on `python:3.12-slim` running as a **non-root** user, which
keeps it reasonably small (~256 MB) and sensible to operate.

---

## Project structure

```
.
├── Dockerfile            # multi-stage, non-root, HEALTHCHECK
├── .dockerignore
├── .github/workflows/ci.yml  # build image, in-image pytest, smoke test
├── requirements.txt      # pinned: fastapi, uvicorn[standard], httpx, pytest
├── README.md
└── src/
    ├── main.py           # FastAPI app: /health, /api/contact, static mount
    ├── test_main.py      # pytest + TestClient tests
    └── web/
        ├── index.html    # hero, about, services, contact, footer
        ├── styles.css    # responsive, mobile-first
        └── app.js        # form fetch() + JP/EN toggle
```

## Run locally without Docker

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cd src && uvicorn main:app --reload --port 8080
```

## Tests

```bash
cd src && pytest          # health 200, contact 200, invalid 422, index served
```

Tests can also run inside the image (pytest ships in it):

```bash
docker run --rm --entrypoint pytest d2future-homepage
```

---

## Features

- Responsive layout, checked at **375px** (phone) and **1440px** (desktop).
- Accessible basics: semantic HTML, labels tied to inputs, visible focus states, skip link.
- **Bilingual JP/EN toggle** (client-side, no dependencies) — appropriate for a Tokyo firm.
- `HEALTHCHECK` using only the Python stdlib (no `curl` in the image).
- **CI** (GitHub Actions): every push builds the image, runs the tests inside it, and
  smoke-tests `/health` and `/api/contact` against a running container.

---

## Assumptions made

The brief invites reasonable assumptions where the spec is open:

- **Port 8080** chosen for HTTP (documented above; avoids privileged port 80 for the
  non-root user).
- **Stack** was my choice (FastAPI) — see rationale above.
- **All marketing copy is invented** (mission, team description, service blurbs). It aims
  for the requested tone: simple, confident, technical, reserved.
- The contact form's "real" action is **logging the payload to stdout** and returning a
  success JSON response, as the brief permits — no email or persistence.
- Email is validated with a light regex rather than the `email-validator` package, to keep
  the image lean (no mail is actually sent).

## Trade-offs / what I'd do with more time

- **Persistence/notifications:** contact submissions only log to stdout. I'd add a queue or
  a webhook (e.g. Slack/email) behind an interface so the storage choice stays swappable.
- **i18n:** the JP/EN toggle uses an inline string map. At scale I'd move copy to JSON
  locale files and persist the choice (localStorage / `Accept-Language`).
- **CI:** the GitHub Actions workflow builds and smoke-tests the image; I'd extend it to
  run `ruff` and publish the image to a registry.
- **Testing:** current tests cover the gates; I'd add a small frontend smoke test
  (Playwright) for the form flow.

## Not finished / out of scope (by design)

Per the brief, the following were intentionally **not** built: Kubernetes manifests, real
email/database, production auth or rate limiting, multi-arch images, and TLS/reverse-proxy.
Exhaustive tests were also out of scope — there are four meaningful tests.

---

*Tooling note: code is formatted and linted with `ruff` (`ruff check . && ruff format .`).*

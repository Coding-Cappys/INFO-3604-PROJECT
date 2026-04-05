# UWI Principal's Research Awards & Festival

A multi-service festival management system for the UWI Principal's Research Awards & Festival. The repository combines a server-rendered Flask application for the primary user experience with a small TypeScript API server and shared workspace libraries.

The platform supports the full conference lifecycle:
- authors submit research
- reviewers evaluate abstracts
- admins make editorial decisions and schedule sessions
- judges score presentations
- attendees RSVP and submit feedback
- ushers check in attendees, including QR-based check-in support

## Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Repository Layout](#repository-layout)
- [Core Features](#core-features)
- [Tech Stack](#tech-stack)
- [User Roles](#user-roles)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Manual Non-Docker Run](#manual-non-docker-run)
- [Render Deployment](#render-deployment)
- [Testing Guide](#testing-guide)
- [Environment Variables](#environment-variables)
- [Known Notes](#known-notes)

## Overview

This codebase is organized as a small workspace with:

- a Flask/Jinja/SQLAlchemy web app in [artifacts/uwi-festival](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/artifacts/uwi-festival)
- a Node/Express API service in [artifacts/api-server](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/artifacts/api-server)
- shared libraries in [lib](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/lib)
- Docker-based local deployment at the repo root

For most local testing, the Flask app is the main application you will interact with in the browser.

## Architecture

### 1. Flask App

The Flask application is the primary user-facing product. It handles:

- authentication and user profiles
- author submissions
- reviewer scoring and comments
- admin scheduling and festival operations
- attendee QR generation, RSVP, and feedback
- usher check-in workflows
- public schedule, awards, and digest pages

Entry point:
- [artifacts/uwi-festival/wsgi.py](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/artifacts/uwi-festival/wsgi.py)

App factory:
- [artifacts/uwi-festival/app/__init__.py](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/artifacts/uwi-festival/app/__init__.py)

### 2. TypeScript API Server

The API service is a separate Express application intended for API-based integration and health checks.

Entry point:
- [artifacts/api-server/src/index.ts](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/artifacts/api-server/src/index.ts)

App setup:
- [artifacts/api-server/src/app.ts](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/artifacts/api-server/src/app.ts)

Health endpoint:
- `GET /api/healthz`

### 3. Shared Libraries

The workspace includes shared libraries for API typing and database access:

- [lib/api-zod](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/lib/api-zod)
- [lib/api-client-react](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/lib/api-client-react)
- [lib/db](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/lib/db)
- [lib/api-spec](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/lib/api-spec)

## Repository Layout

```text
.
├── README.md
├── WORKFLOW.md
├── Dockerfile
├── Dockerfile.api
├── docker-compose.yml
├── pyproject.toml
├── package.json
├── pnpm-workspace.yaml
├── artifacts/
│   ├── uwi-festival/         # Main Flask/Jinja app
│   ├── api-server/           # Express API server
│   └── mockup-sandbox/       # Frontend sandbox artifact
├── lib/
│   ├── api-client-react/
│   ├── api-spec/
│   ├── api-zod/
│   └── db/
└── scripts/
```

### Flask App Structure

```text
artifacts/uwi-festival/
├── wsgi.py
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── attendee.py
│   │   ├── auth.py
│   │   ├── author.py
│   │   ├── judge.py
│   │   ├── public.py
│   │   ├── reviewer.py
│   │   ├── usher.py
│   │   └── utils.py
│   └── templates/
│       ├── admin/
│       ├── attendee/
│       ├── auth/
│       ├── author/
│       ├── judge/
│       ├── public/
│       ├── reviewer/
│       ├── usher/
│       └── base.html
```

## Core Features

### Admin

- view system-wide metrics
- browse and filter submissions
- assign reviewers
- apply editorial decisions
- create venues
- schedule accepted presentations
- assign ushers
- monitor judging and results

### Author

- create an account
- submit new abstracts
- edit submissions before final decisions
- view reviewer/admin feedback
- view scheduled presentation details

### Reviewer

- view assigned submissions
- read submission details
- submit scored reviews
- revisit prior reviews

### Judge

- browse accepted presentations
- score live presentations
- view ranked results

### Attendee

- browse festival schedule
- RSVP to sessions
- generate personal QR code
- leave session feedback

### Usher

- search attendees by ID, email, or name
- check in attendees
- use device camera to scan attendee QR codes
- review session attendance

### Public

- view homepage and schedule
- browse accepted presentations
- view awards
- read the festival digest

## Tech Stack

### Backend

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Gunicorn

### Database

- PostgreSQL in Docker deployment
- SQLite can be used in manual local mode if `DATABASE_URL` is omitted

### Frontend

- Jinja2 templates
- Bootstrap 5
- Bootstrap Icons
- Google Fonts

### QR / Camera

- `qrcode` and Pillow for attendee QR code generation
- browser camera APIs for usher-side scanning
- `jsQR` fallback for browsers without native `BarcodeDetector`

### TypeScript Workspace

- TypeScript
- pnpm workspace
- Express
- esbuild
- Zod
- Drizzle ORM

## User Roles

The app seeds demo users on first startup.

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@uwi.edu` | `admin123` |
| Author | `author@uwi.edu` | `author123` |
| Reviewer | `reviewer@uwi.edu` | `reviewer123` |
| Attendee | `attendee@uwi.edu` | `attendee123` |
| Judge | `judge@uwi.edu` | `judge123` |
| Usher | `usher@uwi.edu` | `usher123` |

## Local Development

### Recommended Option: Docker

This is the easiest and most reliable way to run the full local stack.

Requirements:
- Docker
- Docker Compose

Start everything:

```bash
sudo docker compose up --build
```

Services:
- Flask app: `http://localhost:5000`
- API server: `http://localhost:3001`
- API health endpoint: `http://localhost:3001/api/healthz`

Stop:

```bash
Ctrl+C
```

Bring containers down:

```bash
sudo docker compose down
```

Reset the database volume:

```bash
sudo docker compose down -v
```

### What Docker Starts

- `postgres`
- `uwi-festival`
- `api-server`

Compose definition:
- [docker-compose.yml](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/docker-compose.yml)

Images:
- [Dockerfile](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/Dockerfile)
- [Dockerfile.api](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/Dockerfile.api)

## Docker Deployment

### Build And Run

```bash
sudo docker compose up --build
```

The Dockerfiles are now env-aware for port binding:
- Flask container binds to `${PORT:-5000}`
- API container uses `${PORT:-3001}`

That keeps local Docker behavior unchanged while also making the images safer to reuse on platforms like Render.

### Restart Only The Flask App

```bash
sudo docker compose restart uwi-festival
```

### Follow Logs

All services:

```bash
sudo docker compose logs -f
```

Flask only:

```bash
sudo docker compose logs -f uwi-festival
```

API only:

```bash
sudo docker compose logs -f api-server
```

### Check Service Status

```bash
sudo docker compose ps
```

## Manual Non-Docker Run

This path is useful if you want to work directly on the Flask app without containers.

### Flask App

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-login flask-sqlalchemy flask-wtf gunicorn pillow psycopg2-binary python-dotenv qrcode email-validator werkzeug wtforms
cd artifacts/uwi-festival
export SESSION_SECRET=dev-secret
export PORT=5000
python3 wsgi.py
```

Open:

```text
http://localhost:5000
```

Notes:
- if `DATABASE_URL` is not set, the Flask app falls back to SQLite
- the app seeds demo data on first startup

### TypeScript API Server

Requirements:
- Node.js
- pnpm

From the repo root:

```bash
corepack enable
corepack prepare pnpm@latest --activate
pnpm install
```

Run the API server:

```bash
export PORT=3001
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/uwi_festival
pnpm --filter @workspace/api-server dev
```

Run workspace type checks:

```bash
pnpm run typecheck
```

Build everything:

```bash
pnpm run build
```

## Render Deployment

This repository now includes:

- [requirements.txt](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/requirements.txt)
- [render.yaml](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/render.yaml)

Recommended Render approach:

1. Deploy only the Flask app first.
2. Use a Render PostgreSQL database.
3. Do not rely on SQLite in production-like hosting.

### One-Click Style Setup

If you connect this repo to Render, `render.yaml` defines:
- one free PostgreSQL database
- one free Python web service for the Flask app

### Flask Render Settings

The generated Render service uses:

- Build command:
```bash
pip install -r requirements.txt
```

- Start command:
```bash
cd artifacts/uwi-festival && gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### Why Local Still Works

These Render additions do not replace the local workflow:
- local Docker still uses [docker-compose.yml](/home/jgb/Documents/uwi/yr3sem2/info3604/test/Flask-Jinja-Sqlalchemy/docker-compose.yml)
- the Dockerfiles still default to `5000` and `3001` locally
- local Flask fallback behavior is unchanged

So the repo now supports both:
- local development
- Render deployment

## Testing Guide

### Quick Smoke Test

1. Start the stack with Docker.
2. Open `http://localhost:5000`.
3. Open `http://localhost:3001/api/healthz`.
4. Log in as admin.
5. Visit:
   - `/admin`
   - `/admin/submissions`
   - `/admin/submissions/1`
   - `/admin/agenda`
   - `/admin/results`

### Recommended End-To-End Test Order

1. Author creates a submission.
2. Admin assigns a reviewer.
3. Reviewer submits a review.
4. Admin applies a decision.
5. Admin schedules the submission.
6. Judge submits a score.
7. Attendee RSVPs to a session and opens their QR code.
8. Usher scans or manually checks in the attendee.

### Public Pages To Test

- `/`
- `/schedule`
- `/presentations`
- `/presentations/1`
- `/awards`
- `/digest`

### Browser Checks For QR

For usher QR scanning:
- allow camera permissions
- test in Chrome, Edge, or another modern browser
- if native scanning is unavailable, the app falls back to a compatibility mode using `jsQR`

## Environment Variables

### Flask App

- `PORT`
  - default in Docker: `5000`
- `SESSION_SECRET`
  - required for a non-development deployment
- `DATABASE_URL`
  - in Docker: `postgresql://postgres:postgres@postgres:5432/uwi_festival`
  - local fallback when omitted: SQLite

### API Server

- `PORT`
  - required
- `DATABASE_URL`
  - required by the shared DB library
- `LOG_LEVEL`
  - optional, defaults to `info`

## Known Notes

- The Flask app is the primary product in this repository.
- The API server currently exposes a health route and shared library integration, but the Flask app contains most of the festival workflow logic.
- Demo credentials are seeded for convenience and are not production-safe.
- Local development has recently been hardened to avoid several template/model mismatch errors and bad-input 500s.
- The top-left brand in the authenticated layout acts as the effective "home" link for each role.


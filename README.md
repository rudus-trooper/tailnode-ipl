# IPL Auction API

Dockerized Django REST API for IPL Auction demo. Connects to **AWS RDS MySQL**.

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your RDS credentials
```

### 2. Run with Docker

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
curl -X POST http://localhost:8000/api/populate/
```

---

## GitHub Actions CI/CD Setup

This pipeline runs tests on **EVERY branch** automatically - no configuration needed for new branches!

### Step 1: Add Repository Secrets

Go to **GitHub Repo → Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `DB_NAME` | `ipl_auction` |
| `DB_USER` | `admin` |
| `DB_PASSWORD` | `your_rds_password` |
| `DB_HOST` | `database-1.c9mmuaqii5fl.ap-south-1.rds.amazonaws.com` |
| `DB_PORT` | `3306` |
| `SECRET_KEY` | `any-random-secret-key` |

### Step 2: Enable GitHub Actions

1. Go to **GitHub Repo → Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. That's it! Actions are now enabled

### Step 3: Push Any Branch

```bash
# Create any new branch
git checkout -b feature/my-new-feature
git commit -m "Add new feature"
git push origin feature/my-new-feature

# Pipeline will automatically run!
```

### How It Works

```yaml
on:
  push:
    branches:
      - '**'   # ← This matches ALL branches!
```

| Action | Pipeline Behavior |
|--------|-------------------|
| Push to `main` | ✅ Tests run |
| Push to `develop` | ✅ Tests run |
| Push to `feature/xyz` | ✅ Tests run |
| Push to `hotfix/abc` | ✅ Tests run |
| Create PR from any branch | ✅ Tests run |

---

## Pipeline Stages

```
┌─────────────────────────────────────────────────────────┐
│  1. Checkout Code                                       │
│  2. Set up Python 3.10                                  │
│  3. Install dependencies                                │
│  4. Run migrations (connects to RDS)                    │
│  5. Run tests (connects to RDS)                         │
│  6. Show branch info                                    │
│  7. Build Docker image                                  │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/populate/` | POST | Create teams & players |
| `/api/players/` | GET | List all players |
| `/api/players/active/` | GET | Get active player |
| `/api/players/<id>/bid/` | POST | Place a bid |
| `/api/teams/` | GET | List all teams |

---

## Run Tests Locally

```bash
# Docker
docker compose exec web python manage.py test

# Local
python manage.py test
```

---

## Project Structure

```
ipl_auction/
├── auction/
│   ├── models.py
│   ├── views.py
│   └── tests.py
├── .github/workflows/
│   └── docker-ci.yml      # Runs on ALL branches
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Troubleshooting

### GitHub Actions not running?

1. Check **Settings → Actions → General → Actions permissions**
2. Ensure **"Allow all actions and reusable workflows"** is selected
3. Check if secrets are set correctly

### Can't connect to RDS from GitHub Actions?

1. Verify RDS security group allows GitHub Actions IPs
2. Or temporarily allow `0.0.0.0/0` for testing
3. Check secrets are correctly set in GitHub

```bash
# Test RDS connection
mysql -h database-1.c9mmuaqii5fl.ap-south-1.rds.amazonaws.com \
      -u admin -p ipl_auction
```

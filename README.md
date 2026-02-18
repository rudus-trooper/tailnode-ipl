# IPL Auction API

Dockerized Django REST API for IPL Auction demo. Connects to **AWS RDS MySQL** - no local MySQL needed!

## Quick Start

### 1. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your RDS credentials
nano .env
```

`.env` file:
```bash
DB_NAME=ipl_auction
DB_USER=admin
DB_PASSWORD=your_rds_password
DB_HOST=database-1.c9mmuaqii5fl.ap-south-1.rds.amazonaws.com
DB_PORT=3306
SECRET_KEY=your-secret-key
DEBUG=True
```

### 2. Run with Docker

```bash
# Build and start
docker compose up -d --build

# Run migrations (connects to your RDS)
docker compose exec web python manage.py migrate

# Populate data via API
curl -X POST http://localhost:8000/api/populate/

# Access API
open http://localhost:8000/api/players/
```

### 3. Stop

```bash
docker compose down
```

---

## GitHub Actions CI/CD Setup

### Step 1: Add Repository Secrets

Go to **GitHub Repo → Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DB_NAME` | `ipl_auction` | RDS database name |
| `DB_USER` | `admin` | RDS username |
| `DB_PASSWORD` | `your_password` | RDS password |
| `DB_HOST` | `database-1.c9mmuaqii5fl.ap-south-1.rds.amazonaws.com` | RDS endpoint |
| `DB_PORT` | `3306` | MySQL port |
| `SECRET_KEY` | `your-secret-key` | Django secret key |

### Step 2: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/ipl-auction.git
git push -u origin main
git push origin develop beta prod
```

### Step 3: Verify Pipeline

1. Go to **Actions** tab in GitHub
2. See workflow runs on every push
3. Pipeline connects to your RDS and runs tests

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────┐
│  1. Checkout Code                                       │
│  2. Set up Python 3.10                                  │
│  3. Install dependencies                                │
│  4. Run migrations (connects to RDS)                    │
│  5. Run tests (connects to RDS)                         │
│  6. Build Docker image                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Local Development (without Docker)

### Prerequisites
- Python 3.10+
- Your RDS instance accessible from your IP

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ensure .env has your RDS credentials

# 3. Run migrations (connects to RDS)
python manage.py migrate

# 4. Run server
python manage.py runserver
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/populate/` | POST | Create teams & players with real IPL data |
| `/api/players/` | GET | List all players |
| `/api/players/active/` | GET | Get active player |
| `/api/players/<id>/bid/` | POST | Place a bid |
| `/api/teams/` | GET | List all teams |

### Place a Bid

```bash
curl -X POST http://localhost:8000/api/players/1/bid/ \
  -H "Content-Type: application/json" \
  -d '{"team_id": 1, "amount": 15000000}'
```

---

## Test Cases

```bash
# Docker (connects to RDS)
docker compose exec web python manage.py test

# Local (connects to RDS)
python manage.py test
```

| Category | Test Name | Description |
|----------|-----------|-------------|
| Unit | `test_capped_player_base_price` | Capped = ₹2 Cr base |
| Unit | `test_uncapped_player_base_price` | Uncapped = ₹30 Lakh base |
| Integration | `test_bid_below_base_price_returns_400` | Low bid → 400 |
| Integration | `test_bid_exceeding_purse_returns_400` | Over budget → 400 |
| Integration | `test_bid_on_sold_player_returns_403` | Sold player → 403 |
| Integration | `test_bid_updates_purse` | Purse decreases |
| E2E | `test_complete_auction_flow` | Full auction journey |
| E2E | `test_concurrent_bid_protection` | Race condition handled |
| E2E | `test_aaa_pattern_bid` | Arrange-Act-Assert |

---

## Project Structure

```
ipl_auction/
├── auction/
│   ├── models.py          # Team, Player models
│   ├── views.py           # API views
│   └── tests.py           # Test suite
├── ipl_auction/
│   ├── settings.py        # MySQL config (reads .env)
│   └── urls.py
├── .github/workflows/
│   └── docker-ci.yml      # GitHub Actions (uses RDS)
├── .env.example           # Env template (RDS config)
├── Dockerfile             # App container
├── docker-compose.yml     # Uses .env for RDS
├── manage.py
└── requirements.txt
```

---

## Branch Strategy

```
main      → Stable releases
  ↑
develop   → Active development
  ↑
beta      → Testing/Staging
  ↑
prod      → Production deployments
```

All branches connect to **same RDS** for testing.

---

## Security Notes

- `.env` file is in `.gitignore` - never commit credentials
- GitHub Actions uses **Repository Secrets** for RDS access
- RDS security group should allow GitHub Actions IPs (or use 0.0.0.0/0 for public)
- For production, restrict RDS access to specific IPs only

---

## Troubleshooting

### Can't connect to RDS from local

```bash
# Check RDS security group allows your IP
telnet database-1.c9mmuaqii5fl.ap-south-1.rds.amazonaws.com 3306

# Check .env credentials
cat .env
```

### GitHub Actions can't connect to RDS

1. Verify secrets are set correctly
2. Check RDS security group allows GitHub Actions IP ranges
3. View workflow logs in GitHub Actions tab

```bash
# Test connection manually
mysql -h database-1.c9mmuaqii5fl.ap-south-1.rds.amazonaws.com \
      -u admin -p ipl_auction
```

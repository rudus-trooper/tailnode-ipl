# IPL Auction API

Dockerized Django REST API with MySQL for IPL Auction demo.

## Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed

### Run with Docker Compose

```bash
# 1. Clone and navigate to project
cd ipl-auction

# 2. Start services (MySQL + Django)
docker compose up -d

# 3. Wait for MySQL to initialize (first time takes ~30s)
sleep 30

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Populate data via API
curl -X POST http://localhost:8000/api/populate/

# 6. Access the API
open http://localhost:8000/api/players/
```

### Stop Services

```bash
docker compose down

# To remove all data (including MySQL volume)
docker compose down -v
```

---

## GitHub Actions Setup (Step-by-Step)

### Step 1: Push to GitHub

```bash
# Create GitHub repo first, then:
git remote add origin https://github.com/YOUR_USERNAME/ipl-auction.git
git push -u origin main
git push origin develop
git push origin beta
git push origin prod
```

### Step 2: Verify GitHub Actions File

Ensure `.github/workflows/docker-ci.yml` exists in your repo.

### Step 3: Trigger First Run

Any push to `main`, `develop`, `beta`, or `prod` branches will trigger the pipeline:

```bash
# Make a small change and push
echo "# Test" >> README.md
git add -A
git commit -m "Trigger CI pipeline"
git push origin main
```

### Step 4: View Pipeline Results

1. Go to your GitHub repo
2. Click **Actions** tab
3. See the workflow runs

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────┐
│  1. Checkout Code                                       │
│  2. Set up Docker Buildx                                │
│  3. Build & Start MySQL container                       │
│  4. Build & Start Django container                      │
│  5. Wait for MySQL to be healthy                        │
│  6. Run Django migrations                               │
│  7. Run tests with verbose output                       │
│  8. Test API endpoints                                  │
│  9. Build production Docker image                       │
│  10. Cleanup containers                                 │
└─────────────────────────────────────────────────────────┘
```

---

## Local Development (without Docker)

### 1. Create MySQL Database

```bash
mysql -u root -p -e "CREATE DATABASE ipl_auction;"
```

### 2. Configure Environment

```bash
# Copy and edit .env
cp .env.example .env
nano .env
```

`.env`:
```bash
DB_NAME=ipl_auction
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=your-secret-key
DEBUG=True
```

### 3. Install & Run

```bash
pip install -r requirements.txt
python manage.py migrate
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

Run tests:
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
│   ├── models.py          # Team, Player models
│   ├── views.py           # API views
│   └── tests.py           # Test suite
├── ipl_auction/
│   ├── settings.py        # MySQL config (reads .env)
│   └── urls.py
├── .github/workflows/
│   └── docker-ci.yml      # GitHub Actions pipeline
├── .env.example           # Env template
├── .dockerignore          # Docker ignore rules
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # App container image
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

## CI/CD Environments

| Branch | Docker Environment | Purpose |
|--------|-------------------|---------|
| `main` | Uses docker-compose.yml | Integration testing |
| `develop` | Uses docker-compose.yml | Feature development |
| `beta` | Uses docker-compose.yml | Staging/QA |
| `prod` | Uses docker-compose.yml | Production ready |

---

## Docker Commands Reference

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f

# Run commands in container
docker compose exec web python manage.py shell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py test

# Stop
docker compose down

# Full cleanup
docker compose down -v
docker system prune -a
```

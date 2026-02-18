# IPL Auction API

A Django REST API for IPL player auctions with comprehensive test coverage.

## Features

- Live bidding system with race condition protection
- Team purse management (₹125 Crore budget)
- Player categorization (Capped/Uncapped)
- MySQL ORM with transaction locks
- Docker containerization
- Automated CI/CD with GitHub Actions

## Quick Start

### Prerequisites

- Docker & Docker Compose
- AWS RDS MySQL instance
- GitHub account (for CI/CD)

### Configuration

Create a `.env` file:

```bash
DB_NAME=ipl_auction
DB_USER=admin
DB_PASSWORD=your_rds_password
DB_HOST=your-rds-endpoint.amazonaws.com
DB_PORT=3306
SECRET_KEY=your-secret-key
DEBUG=True
```

### Run Locally

```bash
docker compose up -d
docker compose exec web python manage.py migrate
curl -X POST http://localhost:8000/api/populate/
```

The API is available at `http://localhost:8000`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/populate/` | POST | Seed database with IPL teams and players |
| `/api/players/` | GET | List all players |
| `/api/players/active/` | GET | Get current player under auction |
| `/api/players/<id>/bid/` | POST | Place a bid on a player |
| `/api/teams/` | GET | List all teams with purse balance |

### Place a Bid

```bash
curl -X POST http://localhost:8000/api/players/1/bid/ \
  -H "Content-Type: application/json" \
  -d '{"team_id": 1, "amount": 15000000}'
```

## Testing

```bash
# Run all tests
docker compose exec web python manage.py test

# Run specific test category
docker compose exec web python manage.py test auction.tests.BidIntegrationTest
```

### Test Coverage

| Category | Tests |
|----------|-------|
| Unit | Player base prices, Team purse calculations |
| Integration | Bid validation, Purse updates, Error handling |
| E2E | Complete auction flow, Race condition handling |

## Architecture

```
┌─────────────┐      HTTP       ┌─────────────┐      SQL       ┌─────────────┐
│   Client    │ ──────────────▶ │   Django    │ ──────────────▶ │  AWS RDS    │
│  (Browser)  │ ◀────────────── │    API      │ ◀────────────── │   MySQL     │
└─────────────┘                 └─────────────┘                └─────────────┘
                                       │
                                       ▼
                               ┌─────────────┐
                               │  Docker     │
                               │  Container  │
                               └─────────────┘
```

## CI/CD Pipeline

GitHub Actions runs tests on **every branch** automatically. Workflows use concurrency control to prevent test database conflicts when multiple branches run simultaneously.

### Setup

1. Add repository secrets in GitHub (Settings → Secrets → Actions):
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `SECRET_KEY`

2. Enable GitHub Actions (Actions tab → "Enable workflows")

3. Push any branch - tests run automatically

```bash
git checkout -b feature/new-feature
git push origin feature/new-feature
```

## Project Structure

```
ipl_auction/
├── auction/
│   ├── models.py          # Team, Player models
│   ├── views.py           # API endpoints with transaction locks
│   └── tests.py           # Unit, Integration, E2E tests
├── ipl_auction/
│   ├── settings.py        # Django settings
│   └── urls.py            # URL routing
├── .github/workflows/
│   └── docker-ci.yml      # CI pipeline configuration
├── Dockerfile             # Application container
├── docker-compose.yml     # Service orchestration
└── requirements.txt       # Python dependencies
```

## License

MIT

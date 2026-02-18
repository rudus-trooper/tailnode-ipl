# IPL Auction API

Minimal Django REST API with MySQL for IPL Auction demo.

## Quick Setup

### 1. Create MySQL Database

```bash
mysql -u root -p -e "CREATE DATABASE ipl_auction;"
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your MySQL credentials
nano .env
```

### 3. Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Create migrations and run them
python manage.py makemigrations
python manage.py migrate

# Run server
python manage.py runserver

# Populate data via API (in another terminal)
curl -X POST http://localhost:8000/api/populate/

# Run tests (in another terminal while server is running)
python manage.py test

# Run specific test categories
python manage.py test auction.tests.PlayerBasePriceUnitTest      # Unit tests
python manage.py test auction.tests.BidIntegrationTest            # Integration tests
python manage.py test auction.tests.CompleteAuctionFlowTest       # E2E tests
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/populate/` | POST | Create teams & players with real IPL data |
| `/api/players/` | GET | List all players |
| `/api/players/active/` | GET | Get active player |
| `/api/players/<id>/bid/` | POST | Place a bid |
| `/api/teams/` | GET | List all teams |

## Place a Bid

```bash
curl -X POST http://localhost:8000/api/players/1/bid/ \
  -H "Content-Type: application/json" \
  -d '{"team_id": 1, "amount": 15000000}'
```

## Test Cases (Matches Slides)

| Slide Topic | Test Name |
|-------------|-----------|
| **Unit: Base Price** | `test_capped_player_base_price` (₹2Cr) |
| **Unit: Base Price** | `test_uncapped_player_base_price` (₹30L) |
| **Integration: Validation** | `test_bid_below_base_price_returns_400` |
| **Integration: Security** | `test_bid_exceeding_purse_returns_400` |
| **Integration: State** | `test_bid_on_sold_player_returns_403` |
| **Integration: Purse Update** | `test_bid_updates_purse` |
| **E2E: Full Flow** | `test_complete_auction_flow` |
| **E2E: Race Condition** | `test_concurrent_bid_protection` |
| **E2E: AAA Pattern** | `test_aaa_pattern_bid` |

## Project Structure

```
ipl_auction/
├── auction/
│   ├── models.py          # Team, Player (MySQL via ORM)
│   ├── views.py           # API views with transaction locks
│   └── tests.py           # Unit, Integration, E2E tests
├── ipl_auction/
│   ├── settings.py        # MySQL config
│   └── urls.py
├── manage.py
└── requirements.txt
```

## Configure MySQL Credentials

Edit `ipl_auction/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ipl_auction',
        'USER': 'your_username',      # <-- Change this
        'PASSWORD': 'your_password',  # <-- Change this
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Bid Validation Rules

| Rule | HTTP Status |
|------|-------------|
| Bid < Current Price | 400 Bad Request |
| Bid > Purse Remaining | 400 Bad Request |
| Player Already Sold | 403 Forbidden |

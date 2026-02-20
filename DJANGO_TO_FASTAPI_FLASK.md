# Django (DRF) to FastAPI/Flask Testing Guide

This guide provides equivalents for Django REST Framework testing dependencies when migrating to **FastAPI** or **Flask**.

## Quick Reference Table

| Django (DRF) | FastAPI | Flask |
|--------------|---------|-------|
| `from django.test import TestCase` | `pytest` + `pytest-asyncio` | `pytest` + `pytest-flask` |
| `from rest_framework.test import APIClient` | `httpx.AsyncClient` / `TestClient` | `flask.test_client` |
| `from rest_framework import status` | `fastapi.status` | `http.HTTPStatus` |
| `self.assertEqual()` etc. | `assert` statements (pytest) | `assert` statements (pytest) |
| `Team.objects.create()` | SQLAlchemy + `db_session` | SQLAlchemy / Flask-SQLAlchemy |
| `refresh_from_db()` | `db_session.refresh(obj)` | `db.session.refresh(obj)` |
| `response.data` | `response.json()` | `response.get_json()` |

---

## Detailed Examples

### 1. Test Setup & Client

#### Django:
```python
from django.test import TestCase
from rest_framework.test import APIClient

class MyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
```

#### FastAPI:
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Or sync version
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)
```

#### Flask:
```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client
```

---

### 2. Database/ORM Operations

#### Django:
```python
team = Team.objects.create(name="Team", purse_remaining=1250000000)
player = Player.objects.create(name="Player", base_price=100000000)
team.refresh_from_db()
```

#### FastAPI (SQLAlchemy):
```python
from sqlalchemy.orm import Session

def test_example(db_session: Session):
    team = Team(name="Team", purse_remaining=1250000000)
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)  # equivalent to refresh_from_db()
```

#### Flask (Flask-SQLAlchemy):
```python
from app import db

def test_example(client):
    team = Team(name="Team", purse_remaining=1250000000)
    db.session.add(team)
    db.session.commit()
    db.session.refresh(team)
```

---

### 3. Making HTTP Requests

#### Django:
```python
response = self.client.get('/api/players/active/')
response = self.client.post(f'/api/players/{player.id}/bid/', data)
```

#### FastAPI:
```python
response = await client.get('/api/players/active/')
response = await client.post(f'/api/players/{player.id}/bid/', json=data)
# or sync: client.post(..., json=data)
```

#### Flask:
```python
response = client.get('/api/players/active/')
response = client.post(f'/api/players/{player.id}/bid/', json=data)
```

---

### 4. Assertions

#### Django:
```python
from rest_framework import status
self.assertEqual(response.status_code, status.HTTP_200_OK)
self.assertEqual(response.data['name'], "Rashid Khan")
```

#### FastAPI:
```python
from fastapi import status
assert response.status_code == status.HTTP_200_OK
assert response.json()['name'] == "Rashid Khan"
```

#### Flask:
```python
from http import HTTPStatus
assert response.status_code == HTTPStatus.OK
assert response.get_json()['name'] == "Rashid Khan"
```

---

## Feature Comparison

| Feature | Django | FastAPI | Flask |
|---------|--------|---------|-------|
| **Testing Framework** | Built-in `TestCase` | `pytest` | `pytest` |
| **Test Client** | `APIClient` | `TestClient` / `httpx.AsyncClient` | `app.test_client()` |
| **Database Fixtures** | Built-in transactional tests | `pytest-asyncio-sqlalchemy` / manual setup | `pytest-flask-sqlalchemy` |
| **Async Support** | Limited | Native | Requires `pytest-asyncio` |
| **Status Codes** | `rest_framework.status` | `fastapi.status` | `http.HTTPStatus` |

---

## Recommended Dependencies

### FastAPI:
```txt
pytest
pytest-asyncio
httpx              # Async test client
fastapi[all]       # Includes TestClient
sqlalchemy         # ORM
```

### Flask:
```txt
pytest
pytest-flask
flask-sqlalchemy   # ORM
httpie             # Optional, for testing
```

---

## Original Django Tests (Reference)

See `auction/tests.py` for the original Django tests. Key imports used:

```python
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from auction.models import Team, Player
```

### Test Patterns in Original File

1. **Unit Tests** - `PlayerBasePriceUnitTest`, `TeamPurseUnitTest`
2. **Integration Tests** - `BidIntegrationTest`
3. **E2E Tests** - `CompleteAuctionFlowTest`
4. **Race Condition Tests** - `RaceConditionTest`
5. **AAA Pattern Tests** - `AAAPatternTest`

---

## Migration Tips

### Class-based → Function-based
Django uses class-based tests inheriting from `TestCase`. FastAPI and Flask typically use pytest with **function-based tests**:

```python
# Django (class-based)
class TestPlayer(TestCase):
    def test_create(self):
        pass

# FastAPI/Flask (function-based)
def test_create(client):
    pass
```

### setUp() → Fixtures
Replace Django's `setUp()` method with pytest fixtures:

```python
# Django
def setUp(self):
    self.client = APIClient()
    self.team = Team.objects.create(...)

# FastAPI/Flask
@pytest.fixture
def team(db_session):
    team = Team(...)
    db_session.add(team)
    db_session.commit()
    return team

def test_something(client, team):
    pass
```

### Transactional Tests
- **Django**: Automatic via `TestCase`
- **FastAPI**: Use `pytest-asyncio-sqlalchemy` or wrap in transactions
- **Flask**: Use `pytest-flask-sqlalchemy` or `db.session.rollback()`

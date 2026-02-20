# Django (DRF) to FastAPI/Flask Testing Guide

This guide provides equivalents for Django REST Framework testing dependencies when migrating to **FastAPI** or **Flask**.

## Quick Reference Table

| Django (DRF) | FastAPI | Flask |
|--------------|---------|-------|
| `from django.test import TestCase` | `pytest` + `db_session` fixture | `pytest` + `app_context` |
| `from django.test import SimpleTestCase` | Pure `pytest` (no DB fixtures) | Pure `pytest` (no app context) |
| `from rest_framework.test import APIClient` | `httpx.AsyncClient` / `TestClient` | `flask.test_client` |
| `from rest_framework import status` | `fastapi.status` | `http.HTTPStatus` |
| `self.assertEqual()` etc. | `assert` statements (pytest) | `assert` statements (pytest) |
| `Team.objects.create()` | SQLAlchemy + `db_session` | SQLAlchemy / Flask-SQLAlchemy |
| `refresh_from_db()` | `db_session.refresh(obj)` | `db.session.refresh(obj)` |
| `response.data` | `response.json()` | `response.get_json()` |

---

## SimpleTestCase vs TestCase (Unit vs Integration Tests)

Django provides two main test base classes that differ in database handling:

| Django | Database | Purpose | FastAPI Equivalent | Flask Equivalent |
|--------|----------|---------|-------------------|------------------|
| `SimpleTestCase` | No DB setup | Pure unit tests with mocks | Pure `pytest` functions (no DB fixtures) | Pure `pytest` (no `app_context`) |
| `TestCase` | Creates test DB | Integration tests with ORM | `pytest` with `db_session` fixture | `pytest` with `app_context` + `db.session` |

### Unit Tests (No Database) - SimpleTestCase Pattern

Use when testing pure logic with mocked dependencies.

#### Django:
```python
from django.test import SimpleTestCase
from unittest.mock import Mock

class PlayerUnitTest(SimpleTestCase):  # No database
    def test_base_price_logic(self):
        mock_player = Mock()
        mock_player.is_capped = True
        mock_player.get_min_base_price.return_value = 20000000
        
        result = mock_player.get_min_base_price()
        assert result == 20000000
```

#### FastAPI:
```python
import pytest
from unittest.mock import Mock

# No database fixtures - pure unit test
def test_base_price_logic():
    mock_player = Mock()
    mock_player.is_capped = True
    mock_player.get_min_base_price.return_value = 20000000
    
    result = mock_player.get_min_base_price()
    assert result == 20000000

# Or with patch decorator
from unittest.mock import patch

@patch('app.models.Player')
def test_player_logic(MockPlayer):
    mock_instance = MockPlayer.return_value
    mock_instance.get_min_base_price.return_value = 20000000
    
    player = MockPlayer(name="Test", is_capped=True)
    assert player.get_min_base_price() == 20000000
```

#### Flask:
```python
import pytest
from unittest.mock import Mock, patch

# No app context needed - pure unit test
def test_base_price_logic():
    mock_player = Mock()
    mock_player.is_capped = True
    mock_player.get_min_base_price.return_value = 20000000
    
    result = mock_player.get_min_base_price()
    assert result == 20000000

@patch('app.models.Player')
def test_player_logic(MockPlayer):
    mock_instance = MockPlayer.return_value
    mock_instance.get_min_base_price.return_value = 20000000
    
    player = MockPlayer(name="Test", is_capped=True)
    assert player.get_min_base_price() == 20000000
```

### Integration Tests (With Database) - TestCase Pattern

Use when testing database interactions.

#### Django:
```python
from django.test import TestCase
from auction.models import Player

class PlayerIntegrationTest(TestCase):  # Creates test DB
    def test_player_creation(self):
        player = Player.objects.create(name="Virat", is_capped=True)
        assert player.get_min_base_price() == 20000000
```

#### FastAPI:
```python
import pytest
from sqlalchemy.orm import Session

# With database fixture
@pytest.fixture
def db_session():
    # Setup test database session
    from app.database import SessionLocal
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

def test_player_creation(db_session: Session):
    player = Player(name="Virat", is_capped=True)
    db_session.add(player)
    db_session.commit()
    
    assert player.get_min_base_price() == 20000000
```

#### Flask:
```python
import pytest
from app import create_app, db
from app.models import Player

@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_player_creation(app):
    with app.app_context():
        player = Player(name="Virat", is_capped=True)
        db.session.add(player)
        db.session.commit()
        
        assert player.get_min_base_price() == 20000000
```

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
| **Testing Framework** | Built-in `TestCase`/`SimpleTestCase` | `pytest` | `pytest` |
| **Unit Tests (No DB)** | `SimpleTestCase` | Pure `pytest` + `unittest.mock` | Pure `pytest` + `unittest.mock` |
| **Integration Tests (With DB)** | `TestCase` | `pytest` + `db_session` fixture | `pytest` + `app_context` |
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

### SimpleTestCase vs TestCase Migration
When migrating from Django, separate your tests based on database needs:

```python
# Django - Mixed in one file
class PlayerUnitTest(SimpleTestCase):      # No DB
    pass

class PlayerIntegrationTest(TestCase):     # With DB
    pass

# FastAPI/Flask - Separate by fixtures
# tests/unit/test_player.py (no DB fixtures)
def test_player_logic_unit():
    mock_player = Mock()
    ...

# tests/integration/test_player.py (with DB fixtures)
def test_player_creation(db_session):      # DB fixture injected
    player = Player(name="Test")
    db_session.add(player)
    ...
```

**Key Rule:**
- If test uses `Mock`, `patch` → No DB fixture needed (like `SimpleTestCase`)
- If test uses `Model.objects.create()` → Use DB fixture (like `TestCase`)

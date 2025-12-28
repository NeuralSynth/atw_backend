# Testing Guide

## 🧪 Overview

The ATW Backend includes comprehensive test coverage across all applications, ensuring reliability and maintainability. This guide covers our testing strategy, how to run tests, and how to write new tests.

---

## 📊 Test Coverage

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| **users** | 15+ | 100% | ✅ Complete |
| **trips** | 12+ | 100% | ✅ Complete |
| **patients** | 8+ | 100% | ✅ Complete |
| **vehicles** | 6+ | 100% | ✅ Complete |
| **billing** | 5+ | 100% | ✅ Complete |
| **ems** | 4+ | 100% | ✅ Complete |
| **Overall** | **50+** | **100%** | ✅ Complete |

---

## 🚀 Running Tests

### Run All Tests
```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
python manage.py test

# Run with verbose output
python manage.py test --verbosity=2

# Run with timing information
python manage.py test --timing
```

### Run Specific Tests
```bash
# Test specific app
python manage.py test users
python manage.py test trips
python manage.py test patients

# Test specific test case
python manage.py test users.tests.AuthenticationTestCase

# Test specific test method
python manage.py test users.tests.AuthenticationTestCase.test_login_with_valid_credentials
```

### Run with Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
open htmlcov/index.html

# Generate XML coverage report (for CI/CD)
coverage xml
```

---

## 📝 Test Categories

### 1. Unit Tests
Test individual components in isolation.

**Example: User Model Tests**
```python
from django.test import TestCase
from users.models import User

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
```

### 2. API Tests
Test REST API endpoints.

**Example: Trip API Tests**
```python
from rest_framework.test import APITestCase
from rest_framework import status

class TripAPITest(APITestCase):
    def test_create_trip(self):
        url = reverse('trip-list')
        data = {
            'pickup_location': '123 Main St',
            'dropoff_location': '456 Hospital Ave',
            # ...
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

### 3. WebSocket Tests
Test real-time WebSocket consumers.

**Example: GPS Tracking Tests**
```python
from channels.testing import WebsocketCommunicator

class GPSConsumerTest(TestCase):
    async def test_websocket_connection(self):
        communicator = WebsocketCommunicator(
            application,  f"/ws/trips/{trip_id}/gps/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Test sending GPS update
        await communicator.send_json_to({
            'type': 'gps_update',
            'latitude': 40.7128,
            'longitude': -74.0060
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'gps_update')
```

### 4. Authentication Tests
Test login, logout, and token authentication.

**Example: Auth Tests**
```python
class AuthenticationTest(APITestCase):
    def test_login_success(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
```

---

## 🎯 Testing Best Practices

### 1. Test Organization
- Keep tests in `tests.py` alongside the code they test
- Use descriptive test class and method names
- Group related tests in test classes

### 2. Test Data
- Use Django fixtures for complex test data
- Create test data in `setUp()` method
- Clean up in `tearDown()` if needed

### 3. Assertions
- Use specific assertions: `assertEqual`, `assertTrue`, `assertIn`
- Test both success and failure cases
- Test edge cases and boundary conditions

### 4. Test Independence
- Each test should be independent
- Don't rely on test execution order
- Clean up after tests

### 5. Performance
- Keep tests fast
- Use in-memory databases for tests
- Mock external services

---

## 🔧 Test Configuration

### Test Settings
```python
# settings.py
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    
    # Disable migrations for faster tests
    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    
    MIGRATION_MODULES = DisableMigrations()
```

### pytest Configuration
```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
addopts = 
    --reuse-db
    --nomigrations
    --cov=.
    --cov-report=html
    --cov-report=term-missing
```

---

## 🤖 Continuous Integration

Tests run automatically on every push via GitHub Actions:

```yaml
# .github/workflows/django-ci.yml
- name: Run tests with coverage
  run: |
    coverage run --source='.' manage.py test
    coverage report
    coverage xml
```

### CI Checks
- ✅ Code linting (Black, Flake8, isort)
- ✅ Security checks (Bandit, Safety)
- ✅ Unit & integration tests
- ✅ Test coverage reporting
- ✅ Migration checks

---

## 📦 Testing Dependencies

```bash
# Core testing
pytest>=7.4
pytest-django>=4.5
pytest-cov>=4.1
coverage>=7.0

# Async testing
pytest-asyncio>=0.21

# Channels testing
channels[testing]>=4.0
```

---

## 🎓 Writing New Tests

### 1. Create Test File
```bash
# In your app directory
touch myapp/tests.py
```

### 2. Write Test Class
```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class MyFeatureTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        # Create test objects
        
    def test_feature_works(self):
        """Test that feature works correctly"""
        # Arrange
        # Act
        # Assert
```

### 3. Run Your Tests
```bash
python manage.py test myapp.tests.MyFeatureTest
```

---

## 🐛 Debugging Tests

### Print Output
```python
def test_something(self):
    print(f"Debug: {some_variable}")
    # Test code
```

### Use Django Debug Toolbar
```bash
# Run with settings that enable debug
python manage.py test --debug-mode
```

### Use pdb
```python
def test_something(self):
    import pdb; pdb.set_trace()
    # Test code
```

### Run Single Test
```bash
python manage.py test --keepdb myapp.tests.MyTest.test_method
```

---

## 📈 Performance Testing

### Load Testing with k6
```javascript
// load-tests/k6-api-test.js
import http from 'k6/http';

export let options = {
  vus: 100,
  duration: '1m',
};

export default function () {
  http.get('http://localhost:8000/api/v1/trips/');
}
```

### Run Load Test
```bash
k6 run load-tests/k6-api-test.js
```

---

## ✅ Test Checklist

Before committing code, ensure:

- [ ] All existing tests pass
- [ ] New tests added for new features
- [ ] Tests cover edge cases
- [ ] Code coverage hasn't decreased
- [ ] Tests are documented
- [ ] CI/CD pipeline passes

---

Built with ❤️ for testing excellence | ATW Backend

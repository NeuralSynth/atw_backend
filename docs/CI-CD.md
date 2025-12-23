# CI/CD Pipeline Documentation

## Overview

This document describes the CI/CD pipeline setup for the ATW Backend project using GitHub Actions, Docker, and automated testing.

## Pipeline Architecture

### 🔄 Workflow Stages

```
┌─────────────┐
│   Code Push │
└──────┬──────┘
       │
       ├──────────────────┬───────────────┬──────────────────┐
       │                  │               │                  │
       ▼                  ▼               ▼                  ▼
┌──────────┐    ┌─────────────┐   ┌─────────────┐   ┌────────────┐
│   Lint   │    │    Test     │   │ Migrations  │   │   Build    │
│ & Format │    │ w/ Coverage │   │    Check    │   │   Docker   │
└──────────┘    └─────────────┘   └─────────────┘   └────────────┘
       │                  │               │                  │
       └──────────────────┴───────────────┴──────────────────┘
                                  │
                                  ▼
                          ┌───────────────┐
                          │    Deploy     │
                          │  (if main)    │
                          └───────────────┘
```

## GitHub Actions Workflow

### File: `.github/workflows/django-ci.yml`

#### Jobs

1. **Lint (Code Quality)**
   - Black formatter check
   - isort import sorting
   - Flake8 linting
   - Bandit security scanning
   - Safety dependency vulnerability check

2. **Test**
   - Sets up PostgreSQL service
   - Runs Django migrations
   - Executes test suite with coverage
   - Uploads coverage to Codecov

3. **Migrations Check**
   - Verifies no missing migrations
   - Ensures migrations can run cleanly

4. **Build**
   - Builds Docker image
   - Tests the built image
   - Optionally pushes to Docker Hub

### Triggers

- **Push**: `main`, `develop` branches
- **Pull Request**: to `main`, `develop` branches

## Docker Configuration

### Files

- **`Dockerfile`**: Multi-stage production build
- **`docker-compose.yml`**: Local development stack
- **`.dockerignore`**: Excludes unnecessary files from builds

### Services (Docker Compose)

1. **PostgreSQL** (db)
   - Database service
   - Port: 5432
   - Persistent volume

2. **Redis** (redis)
   - Caching and task queue
   - Port: 6379

3. **Django Web** (web)
   - Main application
   - Port: 8000
   - Auto-migration on startup

4. **Nginx** (optional, production profile)
   - Reverse proxy
   - Port: 80
   - Serves static files

## Local Development with Docker

### Quick Start

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Development Commands

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests
docker-compose exec web python manage.py test

# Access Django shell
docker-compose exec web python manage.py shell

# Collect static files
docker-compose exec web python manage.py collectstatic
```

## Testing Locally

### Without Docker

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run linters
black --check .
flake8 .
isort --check .

# Run tests with coverage
pytest
# or
coverage run -m pytest
coverage report

# Check for security issues
bandit -r .
safety check
```

### With Docker

```bash
# Run tests in container
docker-compose exec web pytest

# With coverage
docker-compose exec web coverage run -m pytest
docker-compose exec web coverage report
```

## Environment Variables

### Required for CI/CD

Set these in your GitHub repository secrets:

- `DOCKER_USERNAME`: Docker Hub username (optional)
- `DOCKER_PASSWORD`: Docker Hub password (optional)

### Local Development

Copy `.env.example` to `.env` and configure:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/atw_db
```

## Deployment

### Docker Deployment

```bash
# Build production image
docker build -t atw-backend:latest .

# Run production container
docker run -d \
  --name atw-backend \
  -p 8000:8000 \
  --env-file .env \
  atw-backend:latest
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start with gunicorn
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 60
```

## Monitoring & Logs

### Docker Logs

```bash
# View all logs
docker-compose logs

# Follow web logs
docker-compose logs -f web

# Follow database logs
docker-compose logs -f db
```

### Health Checks

The Dockerfile includes a health check:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' atw-backend
```

## Troubleshooting

### Common Issues

1. **Tests failing in CI but passing locally**
   - Check PostgreSQL version matches
   - Ensure `.env.example` is up to date
   - Verify migrations are committed

2. **Docker build fails**
   - Check `.dockerignore` is correct
   - Ensure `requirements.txt` is valid
   - Verify base image is accessible

3. **Database connection errors**
   - Check `DATABASE_URL` format
   - Ensure PostgreSQL service is healthy
   - Verify network configuration in docker-compose

### Debug Commands

```bash
# Check Django configuration
python manage.py check

# Test database connection
python manage.py dbshell

# Show migrations status
python manage.py showmigrations

# Validate models
python manage.py validate
```

## Best Practices

### Before Committing

1. Run linters locally:
   ```bash
   black .
   isort .
   flake8 .
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Check migrations:
   ```bash
   python manage.py makemigrations --check
   ```

### Code Quality Standards

- **Coverage**: Minimum 70% test coverage
- **Line Length**: Maximum 127 characters
- **Complexity**: Maximum cyclomatic complexity of 10
- **Security**: No critical Bandit warnings

## CI/CD Optimization Tips

1. **Cache Dependencies**
   - GitHub Actions caches pip packages
   - Docker uses build cache

2. **Parallel Jobs**
   - Lint and test run in parallel
   - Speeds up overall pipeline

3. **Conditional Builds**
   - Docker build only on main/develop
   - Reduces unnecessary builds

## Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)

## Support

For issues with the CI/CD pipeline, please:
1. Check this documentation
2. Review GitHub Actions logs
3. Contact the DevOps team
4. Create an issue in the repository

---

**Last Updated**: 2025-12-23
**Maintained By**: Cyparta Development Team

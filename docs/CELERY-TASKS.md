# Celery Task Queue Guide

## 🔄 Overview

The ATW Backend uses **Celery** for asynchronous task processing, handling everything from GPS updates to invoice generation. This guide covers our Celery architecture, available tasks, and how to work with the task queue system.

---

## 📊 Task Architecture

### Task Queues

We use **3 priority queues** to ensure critical tasks are processed first:

| Queue | Priority | Use Cases | Examples |
|-------|----------|-----------|----------|
| **high_priority** | Highest | Real-time, emergency | GPS broadcasts, status updates |
| **normal** | Medium | Regular operations | Invoice generation, trip completion |
| **low_priority** | Lowest | Non-urgent | Notifications, reports, cleanup |

### Queue Configuration

```python
# config/celery.py
app.conf.task_routes = {
    'trips.tasks.broadcast_gps_update': {'queue': 'high_priority'},
    'trips.tasks.process_trip_completion': {'queue': 'normal'},
    'users.tasks.send_notification': {'queue': 'low_priority'},
}
```

---

## 🎯 Available Tasks

### Trips Module

#### `broadcast_gps_update` (High Priority)
Broadcast GPS location to all clients tracking a trip.

```python
from trips.tasks import broadcast_gps_update

broadcast_gps_update.delay(
    trip_id=123,
    latitude=40.7128,
    longitude=-74.0060,
    speed=45.5,
    heading=180
)
```

#### `broadcast_trip_status` (High Priority)
Notify clients about trip status changes.

```python
from trips.tasks import broadcast_trip_status

broadcast_trip_status.delay(
    trip_id=123,
    status='in_progress',
    message='Driver is on the way'
)
```

#### `process_trip_completion` (Normal)
Handle trip completion workflow (invoice, notifications, vehicle availability).

```python
from trips.tasks import process_trip_completion

process_trip_completion.delay(trip_id=123)
```

#### `cleanup_old_gps_data` (Periodic)
Clean up GPS data older than 30 days.

```python
# Runs automatically via Celery Beat (every hour)
# Manual trigger:
from trips.tasks import cleanup_old_gps_data
cleanup_old_gps_data.delay()
```

#### `check_trip_timeouts` (Periodic)
Flag trips exceeding 6-hour threshold.

```python
# Runs automatically via Celery Beat (every 5 minutes)
# Manual trigger:
from trips.tasks import check_trip_timeouts
check_trip_timeouts.delay()
```

### Billing Module

#### `generate_invoice` (Normal)
Generate invoice for a completed trip.

```python
from billing.tasks import generate_invoice

result = generate_invoice.delay(trip_id=123)
print(result.get())  # Wait for result
```

#### `send_invoice_email` (Low Priority)
Email invoice to patient.

```python
from billing.tasks import send_invoice_email

send_invoice_email.delay(invoice_id=456)
```

#### `process_overdue_invoices` (Periodic)
Process and send reminders for overdue invoices.

```python
# Runs automatically via Celery Beat (daily at 2 AM)
from billing.tasks import process_overdue_invoices
process_overdue_invoices.delay()
```

### Users Module

#### `send_notification` (Low Priority)
Send generic notification to user.

```python
from users.tasks import send_notification

send_notification.delay(
    user_id=789,
    notification_type='trip_assigned',
    message='You have been assigned to Trip #123'
)
```

#### `send_welcome_email` (Low Priority)
Send welcome email to new user.

```python
from users.tasks import send_welcome_email

send_welcome_email.delay(user_id=789)
```

#### `send_trip_assignment_notification` (Normal)
Notify driver about new trip assignment.

```python
from users.tasks import send_trip_assignment_notification

send_trip_assignment_notification.delay(
    trip_id=123,
    driver_id=456
)
```

#### `send_daily_digest` (Periodic)
Send daily digest with trip summary.

```python
# Can be triggered manually or scheduled
from users.tasks import send_daily_digest

send_daily_digest.delay(user_id=789)
```

---

## 🚀 Running Celery

### Start Celery Worker

```bash
# Basic worker (all queues)
celery -A config worker --loglevel=info

# Worker with specific queues
celery -A config worker --queues=high_priority,normal --loglevel=info

# Worker with concurrency
celery -A config worker --concurrency=10 --loglevel=info

# Multiple workers (different terminals)
celery -A config worker --queues=high_priority --loglevel=info -n worker1@%h
celery -A config worker --queues=normal --loglevel=info -n worker2@%h
celery -A config worker --queues=low_priority --loglevel=info -n worker3@%h
```

### Start Celery Beat (Scheduler)

```bash
# Start beat scheduler
celery -A config beat --loglevel=info

# With persistent schedule
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Production Setup

```bash
# Using systemd service files
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# Check status
sudo systemctl status celery-worker
sudo systemctl status celery-beat
```

---

## 📅 Periodic Tasks

Configured in `config/celery.py`:

```python
app.conf.beat_schedule = {
    'cleanup-old-gps-data': {
        'task': 'trips.tasks.cleanup_old_gps_data',
        'schedule': 3600.0,  # Every hour
    },
    'check-trip-timeouts': {
        'task': 'trips.tasks.check_trip_timeouts',
        'schedule': 300.0,  # Every 5 minutes
    },
}
```

### Custom Periodic Task

```python
from celery import shared_task
from celery.schedules import crontab

@shared_task
def my_periodic_task():
    # Your code here
    pass

# Add to config/celery.py
app.conf.beat_schedule['my-task'] = {
    'task': 'myapp.tasks.my_periodic_task',
    'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
}
```

---

## 🔍 Monitoring Tasks

### Inspect Active Tasks

```bash
# View active tasks
celery -A config inspect active

# View registered tasks
celery -A config inspect registered

# View scheduled tasks
celery -A config inspect scheduled

# View worker stats
celery -A config inspect stats
```

### Control Tasks

```bash
# Revoke a task
celery -A config revoke <task_id>

# Purge all tasks
celery -A config purge

# Purge specific queue
celery -A config purge -Q high_priority
```

### Monitor with Flower

```bash
# Install Flower
pip install flower

# Start Flower dashboard
celery -A config flower

# Access at http://localhost:5555
```

---

## 🧪 Testing Tasks

### Test Task Execution

```python
# tests.py
from django.test import TestCase
from trips.tasks import broadcast_gps_update

class TaskTest(TestCase):
    def test_broadcast_gps_update(self):
        # Execute task synchronously  in tests
        result = broadcast_gps_update.apply(
            args=[123, 40.7128, -74.0060],
            kwargs={'speed': 45.5}
        )
        
        self.assertIn('GPS update broadcast', result.result)
```

### Debug Mode

```python
# Force synchronous execution
from celery import current_app
current_app.conf.task_always_eager = True
```

---

## ⚙️ Configuration

### Broker Settings

```python
# config/settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
```

### Task Settings

```python
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 28 * 60  # 28 minutes
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # 1 minute
```

### Optimization

```python
CELERY_TASK_COMPRESSION = 'gzip'
CELERY_RESULT_COMPRESSION = 'gzip'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
```

---

## 📈 Performance Tuning

### Auto-Scaling Workers

```yaml
# k8s/deployments/celery-worker.yaml
spec:
  replicas: 10
  
# k8s/autoscaling/hpa-celery.yaml
spec:
  minReplicas: 10
  maxReplicas: 100
  metrics:
  - type: External
    external:
      metric:
        name: celery_queue_length
      target:
        type: Value
        value: "100"
```

### Queue Length Monitoring

```python
# Get queue length
from celery import current_app

def get_queue_length(queue_name):
    with current_app.connection_or_acquire() as conn:
        return conn.default_channel.queue_declare(
            queue=queue_name, passive=True
        ).message_count
```

---

## 🐛 Troubleshooting

### Task Not Executing

1. Check worker is running:
   ```bash
   celery -A config inspect active
   ```

2. Check queue routing:
   ```python
   # Verify task route
   from config.celery import app
   print(app.conf.task_routes)
   ```

3. Check broker connection:
   ```bash
   redis-cli ping
   ```

### Task Failures

View failed tasks:
```bash
celery -A config inspect failed
```

Retry failed task:
```python
result.retry(countdown=60)
```

---

## ✅ Best Practices

1. **: Always use `.delay()` or `.apply_async()`
2. **Idempotent**: Tasks should be safe to run multiple times
3. **Timeouts**: Set reasonable time limits
4. **Retries**: Implement retry logic for transient failures
5. **Logging**: Add logging for debugging
6. **Error Handling**: Handle exceptions gracefully
7. **Results**: Only store results if needed (saves memory)

---

Built with ❤️ for async processing | ATW Backend

# ATW Backend - All The Way Transportation System

Backend service for the **All The Way (ATW) Transportation System**, developed by Cyparta. This Django-based system manages ambulance dispatch, patient records, vehicle tracking, medical compliance, and billing operations.

## 🚀 Technology Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Session/Basic (DRF)
- **ORM**: Django ORM
- **CORS**: django-cors-headers
- **Environment Management**: python-dotenv

## 📁 Project Structure

```
atw_backend/
├── config/                 # Django project configuration
│   ├── settings.py        # Main settings file
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI application
│
├── users/                  # User management & authentication
│   ├── models.py          # Custom User model with roles
│   ├── views.py           # User API endpoints
│   ├── serializers.py     # User data serialization
│   └── management/        # Management commands
│       └── commands/
│           └── populate_sample_data.py
│
├── patients/               # Patient records management
│   ├── models.py          # Patient model
│   ├── views.py           # Patient CRUD endpoints
│   └── serializers.py     # Patient serialization
│
├── vehicles/               # Fleet & vehicle management
│   ├── models.py          # Vehicle, GPS tracking
│   ├── views.py           # Vehicle API endpoints
│   └── serializers.py     # Vehicle serialization
│
├── trips/                  # Trip dispatch & tracking
│   ├── models.py          # Trip model
│   ├── views.py           # Trip endpoints
│   └── serializers.py     # Trip serialization
│
├── ems/                    # EMS compliance & reporting
│   ├── models.py          # Medical compliance models
│   ├── views.py           # EMS report endpoints
│   └── serializers.py     # EMS serialization
│
├── billing/                # Invoicing & contracts
│   ├── models.py          # Billing, Invoice models
│   ├── views.py           # Billing endpoints
│   └── serializers.py     # Billing serialization
│
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in version control)
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🎯 Core Features

### User Management
- Custom user model with role-based access (Admin, Driver, Medic, Dispatcher)
- Authentication via Django session/basic auth
- User profile management

### Patient Records
- Comprehensive patient information management
- Medical history and condition tracking
- HIPAA-compliant data handling

### Vehicle & Fleet Management
- Real-time vehicle tracking
- Vehicle status and availability
- Maintenance scheduling
- GPS location tracking

### Trip Dispatch
- Ambulance dispatch system
- Trip assignment and routing
- Real-time status updates
- Trip history and analytics

### EMS Compliance
- Medical compliance reporting
- Incident documentation
- Regulatory compliance tracking

### Billing & Invoicing
- Contract management
- Invoice generation
- Payment tracking
- Financial reporting

## 🛠️ Setup & Installation

### Prerequisites

- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **pip**: Latest version
- **virtualenv**: For creating isolated Python environments

### 1. Clone the Repository

```bash
git clone <repository-url>
cd atw_backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/atw_db

# CORS Settings (optional)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password

# Static/Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
```

> **Note**: Copy `.env.example` to `.env` and update the values for your environment.

### 5. Database Setup

#### Create PostgreSQL Database

```bash
# Using psql
psql -U postgres
CREATE DATABASE atw_db;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE atw_db TO your_username;
\q
```

#### Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. (Optional) Populate Sample Data

```bash
python manage.py populate_sample_data
```

This will create sample users, patients, vehicles, trips, and billing records for testing.

### 8. Run Development Server

```bash
python manage.py runserver
```

The application will be available at:
- **API**: http://localhost:8000/api/v1/
- **Admin Panel**: http://localhost:8000/admin/

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1/
```

### Available Endpoints

#### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout

#### Users
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/{id}/` - Get user details
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user

#### Patients
- `GET /api/v1/patients/` - List all patients
- `POST /api/v1/patients/` - Create new patient
- `GET /api/v1/patients/{id}/` - Get patient details
- `PUT /api/v1/patients/{id}/` - Update patient
- `DELETE /api/v1/patients/{id}/` - Delete patient

#### Vehicles
- `GET /api/v1/vehicles/` - List all vehicles
- `POST /api/v1/vehicles/` - Register new vehicle
- `GET /api/v1/vehicles/{id}/` - Get vehicle details
- `PUT /api/v1/vehicles/{id}/` - Update vehicle
- `DELETE /api/v1/vehicles/{id}/` - Delete vehicle

#### Trips
- `GET /api/v1/trips/` - List all trips
- `POST /api/v1/trips/` - Create new trip
- `GET /api/v1/trips/{id}/` - Get trip details
- `PUT /api/v1/trips/{id}/` - Update trip
- `DELETE /api/v1/trips/{id}/` - Delete trip

#### EMS
- `GET /api/v1/ems/` - List EMS reports
- `POST /api/v1/ems/` - Create EMS report
- `GET /api/v1/ems/{id}/` - Get report details

#### Billing
- `GET /api/v1/billing/` - List invoices
- `POST /api/v1/billing/` - Create invoice
- `GET /api/v1/billing/{id}/` - Get invoice details

## 🧪 Development

### Running Tests

```bash
python manage.py test
```

### Create Django App

```bash
python manage.py startapp app_name
```

### Make Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect Static Files

```bash
python manage.py collectstatic
```

### Django Shell

```bash
python manage.py shell
```

## 🔒 Security Notes

- **Never commit `.env` file** to version control
- **Change `SECRET_KEY`** in production
- **Set `DEBUG=False`** in production
- **Use strong passwords** for database and superuser accounts
- **Enable HTTPS** in production
- **Configure proper CORS** settings for production

## 📝 Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEBUG` | Enable debug mode | `False` | ✅ |
| `SECRET_KEY` | Django secret key | - | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost` | ⚠️ (prod) |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | - | ❌ |
| `EMAIL_HOST` | Email SMTP server | - | ❌ |
| `EMAIL_PORT` | Email server port | `587` | ❌ |
| `EMAIL_HOST_USER` | Email username | - | ❌ |
| `EMAIL_HOST_PASSWORD` | Email password | - | ❌ |

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

## 📄 License

See the [LICENSE](LICENSE) file for details.

## 👥 Team

Developed by **Cyparta** - All The Way Transportation System

---

For issues or questions, please contact the development team.

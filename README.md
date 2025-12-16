# ATW Backend - All The Way Transportation System

Backend service for the All The Way (ATW) Transportation System, developed by Cyparta. This system manages ambulance dispatch, patient records, vehicle tracking, and billing.

## Technology Stack
- **Framework**: Django & Django REST Framework
- **Database**: PostgreSQL
- **ORM**: Django ORM
- **Authentication**: Session / Basic (Configurable JWT)

## System Architecture
The backend is structured into modular Django Apps:
- **users**: Identity & Roles (Admin, Driver, Medic, etc.)
- **vehicles**: Fleet management.
- **trips**: Dispatch engine & Chat.
- **patients**: Medical records.
- **ems**: Medical compliance reports.
- **billing**: Invoicing & Contracts.

## Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL

### 1. Installation
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Database Configuration
Ensure your `.env` file is set up:
```env
DATABASE_URL=postgresql://neuralsynth:password@localhost/atw_db_v2
```

### 3. Initialize Database
```bash
python manage.py migrate
```

### 4. Create Admin User
```bash
python manage.py createsuperuser
```

### 5. Running the Server
Start the development server:
```bash
python manage.py runserver
```
The API will be available at [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/).
The Admin interface is at [http://localhost:8000/admin/](http://localhost:8000/admin/).


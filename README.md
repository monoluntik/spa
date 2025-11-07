
---

# Spy Cat Agency Management System

A Django REST API for managing spy cats, their missions, and targets.


## Tech Stack

* Django 4.2+
* Django REST Framework
* PostgreSQL (via Docker Compose)
* TheCatAPI for breed validation

---

## Installation

### Prerequisites

* Docker & Docker Compose installed

### Setup

1. Clone the repository:

```bash
git git@github.com:monoluntik/spa.git
cd spa
```

2. Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Edit `.env` to match your configuration (database credentials, secret key, debug mode, etc.)

Example `.env` for Docker Compose:

```
POSTGRES_DB=db
POSTGRES_USER=db
POSTGRES_PASSWORD=db
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEBUG=True
SECRET_KEY=django-insecure-very-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

3. Build and run Docker containers:

```bash
docker compose up --build
```

This will:

* Start PostgreSQL database (`db` service)
* Apply Django migrations
* Start Django development server (`web` service) on `http://localhost:8000/`

4. (Optional) Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

---

## API Endpoints

### Spy Cats

* `GET /api/cats/` - List all spy cats
* `POST /api/cats/` - Create a new spy cat
* `GET /api/cats/{id}/` - Get a single spy cat
* `PATCH /api/cats/{id}/` - Update spy cat (salary only)
* `DELETE /api/cats/{id}/` - Delete a spy cat

### Missions

* `GET /api/missions/` - List all missions
* `POST /api/missions/` - Create a new mission with targets
* `GET /api/missions/{id}/` - Get a single mission
* `DELETE /api/missions/{id}/` - Delete a mission (only if not assigned)
* `POST /api/missions/{id}/assign_cat/` - Assign a cat to a mission
* `PATCH /api/missions/{id}/update_target/` - Update target notes/completion

---

## API Usage Examples

### Create a Spy Cat

```bash
POST /api/cats/
{
  "name": "Shadow",
  "years_of_experience": 5,
  "breed": "Siamese",
  "salary": 50000.00
}
```

### Update Spy Cat Salary

```bash
PATCH /api/cats/1/
{
  "salary": 55000.00
}
```

### Create a Mission with Targets

```bash
POST /api/missions/
{
  "cat": null,
  "targets": [
    {
      "name": "Target Alpha",
      "country": "USA",
      "notes": "High priority target"
    },
    {
      "name": "Target Beta",
      "country": "UK",
      "notes": "Secondary target"
    }
  ]
}
```

### Assign Cat to Mission

```bash
POST /api/missions/1/assign_cat/
{
  "cat_id": 1
}
```

### Update Target Notes

```bash
PATCH /api/missions/1/update_target/
{
  "target_id": 1,
  "notes": "Target located. Surveillance in progress."
}
```

### Mark Target as Complete

```bash
PATCH /api/missions/1/update_target/
{
  "target_id": 1,
  "complete": true
}
```

---

## Admin Panel

Access the Django admin panel at:

```
http://localhost:8000/admin/
```


# Contributing

## Development Setup
1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python -m imagen_desktop.main
```

## Development

### Database Migrations
Always run database migrations before starting development:
```bash
alembic upgrade head
```

When making database schema changes:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```
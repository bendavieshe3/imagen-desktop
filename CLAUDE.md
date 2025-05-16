# Imagen Desktop Project

## Project Overview
Imagen Desktop is a PyQt6-based desktop application for running generative AI models, with a focus on image generation using Replicate's API.

## Project Structure
- `/imagen_desktop/` - Main package directory
  - `/api/` - API client for Replicate
  - `/core/` - Core application logic and events
    - `/config/` - Application configuration
    - `/events/` - Event system for inter-component communication
    - `/models/` - Domain models (Generation, Order, Product)
  - `/data/` - Database, models, and repositories
    - `/migrations/` - Alembic database migrations
    - `/repositories/` - Data access layer
    - `/schema/` - SQLAlchemy models
  - `/ui/` - User interface components
    - `/features/` - UI feature modules
      - `/gallery/` - Gallery management and display
      - `/generation/` - Generation form and controls
    - `/shared/` - Reusable UI components
  - `/utils/` - Utility functions

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

## Development Workflow
1. Make sure to set up your Replicate API key in a `.env` file:
```
REPLICATE_API_TOKEN=your_api_token_here
```
   
   Alternatively, you can store it in a config file:
   ```json
   // at ~/.imagen-desktop/config.json
   {
     "api_key": "your_api_token_here"
   }
   ```

2. Always run database migrations before starting development:
```bash
alembic upgrade head
```

3. When making database schema changes:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Cost Considerations
This application connects to Replicate's API for generating images. Please be aware:

1. Running image generation models via Replicate incurs costs based on usage
2. You need a valid Replicate API key with associated billing information
3. Each model has different pricing - check Replicate documentation for specific costs
4. Consider implementing user-facing limits or warnings about potential costs
5. When testing, prefer smaller batch sizes and fewer parameters to minimize costs

## Commands
### Run Application
```bash
python -m imagen_desktop.main
```

### Testing
```bash
python -m unittest discover -s tests
```

### Database Migrations
```bash
alembic upgrade head
```

## Coding Standards
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Use docstrings for classes and public methods
- Use domain-driven design principles
- Prefer composition over inheritance
- Follow the presenter-first architecture for UI components

## Git Workflow
- Create feature branches from master
- Keep commits focused on single logical changes
- Use descriptive commit messages with present tense verbs
- Run tests before pushing changes
- Rebase feature branches on master before merging

## TODO Items
See [TODO.md](/Volumes/Ceres/data/Projects/imagen/TODO.md) for current tasks.

## Stack
- UI: PyQt6
- API: Replicate client
- Database: SQLAlchemy with SQLite
- Migration: Alembic
- Image Processing: Pillow
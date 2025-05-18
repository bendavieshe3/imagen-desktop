# Technology

## Detailed Technology Stack

Remember to update [CLAUDE.md](../CLAUDE.md) and [README.md](../README.md) with a succinct summary

The product is coded in Python and runs in a virtual environment. 

- UI: PyQt6
- API: Replicate client
- Database: SQLAlchemy with SQLite
- Migration: Alembic
- Testing: pytest
- Image Processing: Pillow

## Technical Decisions

### 1. Qt Implementation
- Use of Qt's Model/View architecture
- Custom widgets for specialized functionality
- Stylesheet-based theming
- Cross-platform compatibility considerations

### 2. API Integration
- Asynchronous API calls
- Request queuing system
- Response parsing and validation
- Webhook support (if needed)

### 3. Storage
- SQLite database for metadata
- File system organization for images
- Caching strategy
- Backup system

### 4. Event strategy
- QT signals for UI management, domain events for application/business events

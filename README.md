# Knowledge Pathways Backend

A backend API service for managing educational knowledge pathways and learning journeys.

## Features

- User authentication and authorization
- Knowledge pathway management
- Learning progress tracking
- Content management system
- API endpoints for frontend integration

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **ORM**: SQLAlchemy
- **Testing**: pytest
- **Documentation**: OpenAPI/Swagger

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Installation

1. **Install Python**: Download and install Python from [python.org](https://www.python.org/downloads/)

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd knowledge-pathways-backend
   ```

3. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

4. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

7. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

8. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
knowledge-pathways-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── api/
│   ├── core/
│   └── utils/
├── alembic/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Lint code: `flake8`
- Type checking: `mypy .`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

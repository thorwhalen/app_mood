# Development Guide

## Implementation Status

### Phase 1: Foundation ✅ (Completed)

The following components have been implemented:

### Backend ✅
- [x] FastAPI application setup
- [x] PostgreSQL database schema
- [x] SQLAlchemy models (Mood, Dataset, MLModel, Analysis, Task, User)
- [x] Pydantic schemas for validation
- [x] CRUD API endpoints for moods
- [x] Dataset generation endpoints
- [x] Model training endpoints
- [x] Analysis endpoints
- [x] Celery configuration for async tasks
- [x] OpenAI integration wrapper

### Frontend ✅
- [x] React + TypeScript + Vite setup
- [x] Material-UI integration
- [x] React Query for data fetching
- [x] API client service
- [x] Navigation component
- [x] Home page
- [x] Moods page (CRUD operations)
- [x] Mood detail page (datasets & models)
- [x] Analysis page
- [x] Headlines page
- [x] History page

### Infrastructure ✅
- [x] Docker Compose configuration
- [x] PostgreSQL container
- [x] Redis container
- [x] Backend Dockerfile
- [x] Frontend Dockerfile
- [x] Celery worker container

### Testing ✅
- [x] Pytest configuration
- [x] Backend unit tests
- [x] Backend integration tests
- [x] Playwright E2E tests
- [x] Test fixtures and utilities
- [x] CI/CD pipeline (GitHub Actions)

### Phase 2: Mood Library Integration ✅ (Completed)

Full integration with the mood library ML pipeline:

1. ✅ **Real Dataset Generation** (`backend/app/services/dataset_service.py`)
   - OpenAI-powered training example generation
   - Semantic attribute-based text creation
   - Stores actual examples with scores 0-5

2. ✅ **Real Model Training** (`backend/app/services/training_service.py`)
   - `MoodModelingManager` for training
   - Embedding computation via OpenAI
   - Multiple model types (regression, classification, ordinal)
   - Real metrics (Spearman, MAE, RMSE, F1)
   - Automatic best model selection

3. ✅ **Real Analysis** (`backend/app/services/analysis_service.py`)
   - Trained model inference
   - Embedding-based predictions
   - Normalized scores 0-1

4. ✅ **Real Headlines** (`backend/app/services/analysis_service.py`)
   - Multi-tier fallback (mood library → OpenAI → mock)
   - Financial sentiment analysis
   - Scores from -10 to +10

**See `PHASE2_NOTES.md` for detailed integration documentation, testing guide, and troubleshooting.**

### Development Workflow

#### Running Locally

```bash
# Start all services
docker-compose up

# Or run individually for development
# Terminal 1 - Database
docker-compose up db redis

# Terminal 2 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3 - Celery
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 4 - Frontend
cd frontend
npm run dev
```

#### Making Changes

1. **Backend changes**:
   - Edit files in `backend/app/`
   - Hot reload is enabled with `--reload` flag

2. **Frontend changes**:
   - Edit files in `frontend/src/`
   - Vite provides instant HMR (Hot Module Replacement)

3. **Database changes**:
   - Create Alembic migration (future enhancement)
   - For now, changes require rebuilding the database

#### Testing Changes

```bash
# Backend tests
cd backend
pytest

# Specific test file
pytest tests/unit/test_moods.py

# With coverage
pytest --cov=app

# E2E tests (services must be running)
cd tests/e2e
pytest

# Specific test
pytest test_mood_lifecycle.py::test_create_mood_user_story
```

### Code Organization

#### Backend Service Layer

Services handle business logic and are used by both API endpoints and Celery tasks:

- `dataset_service.py`: Dataset generation logic
- `training_service.py`: Model training logic
- `analysis_service.py`: Text analysis logic

#### Frontend Patterns

- **Pages**: Full page components in `frontend/src/pages/`
- **Components**: Reusable UI components in `frontend/src/components/`
- **Services**: API client functions in `frontend/src/services/`
- **Types**: TypeScript interfaces in `frontend/src/types/`

#### Adding New Features

1. **Define the model** in `backend/app/models/`
2. **Create the schema** in `backend/app/schemas/`
3. **Implement the service** in `backend/app/services/`
4. **Add API endpoint** in `backend/app/api/`
5. **Create TypeScript types** in `frontend/src/types/`
6. **Add API client method** in `frontend/src/services/api.ts`
7. **Create UI components** in `frontend/src/`
8. **Write tests** in `backend/tests/` and `tests/e2e/`

### Database Migrations (Future)

Currently using `Base.metadata.create_all()` for simplicity. For production:

```bash
# Initialize Alembic
cd backend
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Environment Variables

See `.env.example` for all available configuration options.

Critical variables:
- `OPENAI_API_KEY`: Required for dataset generation
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: For JWT tokens (production)

### Debugging

#### Backend Debugging

Add breakpoints using `import pdb; pdb.set_trace()`

Or use VS Code debugger with this `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

#### Frontend Debugging

Use browser DevTools:
- React DevTools extension
- Network tab for API calls
- Console for errors

### Performance Considerations

1. **Database queries**: Add indexes for frequently queried fields
2. **API pagination**: Implemented with `skip` and `limit` parameters
3. **Large datasets**: Consider streaming responses
4. **Celery tasks**: Monitor queue length and worker capacity

### Security Checklist

- [ ] Implement authentication (OAuth2/JWT)
- [ ] Add rate limiting
- [ ] Validate all inputs
- [ ] Sanitize outputs (XSS prevention)
- [ ] Use HTTPS in production
- [ ] Rotate SECRET_KEY
- [ ] Implement CSRF protection
- [ ] Add API key management for OpenAI keys

### Deployment Checklist

- [ ] Set production environment variables
- [ ] Configure cloud database (RDS, Cloud SQL)
- [ ] Set up cloud storage (S3, GCS)
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging aggregation
- [ ] Configure auto-scaling
- [ ] Set up backup strategy
- [ ] Configure CDN for frontend
- [ ] Enable HTTPS/TLS
- [ ] Set up CI/CD pipeline

## Troubleshooting

### Common Issues

**Database connection errors**
```bash
# Check if PostgreSQL is running
docker-compose ps db

# View logs
docker-compose logs db
```

**Frontend can't connect to backend**
```bash
# Check proxy configuration in vite.config.ts
# Ensure backend is running on port 8000
```

**Celery tasks not executing**
```bash
# Check Celery worker logs
docker-compose logs celery

# Check Redis connection
docker-compose ps redis
```

**Tests failing**
```bash
# Clean test database
docker-compose down -v
docker-compose up -d

# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Material-UI](https://mui.com/)
- [Playwright](https://playwright.dev/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Mood Library](https://github.com/thorwhalen/mood)

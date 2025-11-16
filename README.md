# app_mood

A full-stack web application for financial sentiment analysis using the [mood](https://github.com/thorwhalen/mood) library.

## Features

- **Define Custom Moods**: Create semantic attributes to detect specific sentiments in financial text
- **Generate Training Data**: AI-powered dataset generation using OpenAI GPT-4
- **Train ML Models**: Automatically train and compare multiple model types using mood's `MoodModelingManager`
- **Analyze Text**: Get real sentiment scores (0-1) for individual texts or batches
- **Financial Headlines**: Quick analysis of current financial news with sentiment scores
- **Analysis History**: Track and visualize sentiment trends over time

**✨ Phase 2 Complete**: Fully integrated with the mood library ML pipeline for real sentiment analysis.

## Architecture

### Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React + TypeScript + Vite + Material-UI
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis
- **Testing**: Pytest + Playwright

### Services

- `backend`: FastAPI REST API
- `frontend`: React SPA
- `celery`: Background task worker
- `db`: PostgreSQL database
- `redis`: Message broker and cache

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (for dataset generation and headline analysis)

### Quick Start

1. **Clone the repository**

```bash
git clone <repository-url>
cd app_mood
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Start the services**

```bash
docker-compose up --build
```

4. **Access the application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Setup

#### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

#### Running Tests

**Backend Tests (Pytest)**

```bash
cd backend
pytest
```

**E2E Tests (Playwright)**

```bash
# Make sure services are running
docker-compose up

# Install Playwright browsers (first time only)
cd tests/e2e
pip install -r requirements.txt
playwright install

# Run E2E tests
pytest
```

## Usage Guide

### 1. Create a Mood

1. Navigate to the **Moods** page
2. Click **Create Mood**
3. Fill in:
   - **Name**: e.g., "Bullish Sentiment"
   - **Description**: e.g., "Optimistic market outlook"
   - **Attribute Definition**: e.g., "Text expressing positive expectations about market performance"
4. Click **Create**

### 2. Generate Training Dataset

1. Go to your mood's detail page
2. Click **Generate Dataset**
3. Wait for generation to complete (uses OpenAI API)
4. View the generated examples in the dataset

### 3. Train Models

1. On the mood detail page, go to the **Datasets** tab
2. Click **Train Models** on a completed dataset
3. Wait for training to complete
4. View model metrics in the **Models** tab
5. Select the best performing model

### 4. Analyze Text

1. Navigate to the **Analysis** page
2. Select a mood (must have a trained model)
3. Enter text to analyze
4. Click **Analyze** to get a sentiment score (0-1)

### 5. View Financial Headlines

1. Navigate to the **Headlines** page
2. View current financial headlines with sentiment scores (-10 to +10)

### 6. Browse History

1. Navigate to the **History** page
2. Filter by mood to see past analyses
3. Track sentiment trends over time

## API Documentation

The API is fully documented with OpenAPI/Swagger. Access it at:

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```
# Moods
POST   /api/v1/moods              # Create mood
GET    /api/v1/moods              # List moods
GET    /api/v1/moods/{id}         # Get mood
PUT    /api/v1/moods/{id}         # Update mood
DELETE /api/v1/moods/{id}         # Delete mood

# Datasets
POST   /api/v1/datasets/{mood_id}/generate  # Generate dataset

# Models
POST   /api/v1/models/{mood_id}/train       # Train models
POST   /api/v1/models/{id}/select           # Select model

# Analysis
POST   /api/v1/analysis           # Analyze text
POST   /api/v1/analysis/batch     # Batch analysis
GET    /api/v1/analysis/headlines # Financial headlines
GET    /api/v1/analysis           # Analysis history
```

## Project Structure

```
app_mood/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── tasks/       # Celery tasks
│   │   └── utils/       # Utilities
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Page components
│       ├── services/    # API client
│       └── types/       # TypeScript types
├── tests/
│   └── e2e/            # Playwright E2E tests
└── docker-compose.yml  # Docker orchestration
```

## Testing Strategy

### Test Pyramid

1. **Unit Tests** (Pytest): Business logic and utility functions
2. **API Tests** (Pytest + TestClient): API endpoint integration
3. **E2E Tests** (Playwright): Full user journeys

### User Stories Tested

- ✅ Create and manage mood definitions
- ✅ Generate training datasets
- ✅ Train and compare models
- ✅ Analyze single texts
- ✅ Batch analysis
- ✅ View financial headlines
- ✅ Browse analysis history

## Cloud Deployment

The application is designed to be cloud-ready:

### Environment-Based Configuration

All environment-specific settings are configured via environment variables.

### Kubernetes Deployment

```bash
# Build and push images
docker build -t your-registry/mood-backend:latest ./backend
docker build -t your-registry/mood-frontend:latest ./frontend
docker push your-registry/mood-backend:latest
docker push your-registry/mood-frontend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Cloud Storage

For production, configure object storage:

```env
STORAGE_TYPE=s3
S3_BUCKET=your-bucket-name
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the mood library documentation

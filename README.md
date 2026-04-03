# GiftPedia - AI-Powered Gift Recommendation System

## Overview
GiftPedia is an intelligent gift recommendation system that uses multi-agent AI architecture to help users find perfect gifts. The system builds user confidence by providing personalized, well-explained recommendations using Google Gemini API and vector similarity search.

## Architecture
- **Frontend**: Next.js with TypeScript
- **Backend**: FastAPI with Python
- **AI**: Google Gemini Flash API (4 specialized agents)
- **Vector Database**: Pinecone (product embeddings)
- **Database**: PostgreSQL (user data, analytics)

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Google Gemini API key
- Pinecone API key

### Installation

#### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API configuration
npm run dev
```

#### Backend Setup
```bash
cd api
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py
```

### Automated Setup (Recommended)

For easy setup and testing, run the automated setup script:

```bash
python setup_manual_testing.py
```

This script will:
- ✅ Check all requirements
- ✅ Install dependencies
- ✅ Create environment files
- ✅ Start both servers
- ✅ Open the application in your browser

### Manual Testing

Once servers are running:

1. **Frontend**: http://localhost:3000
   - Main application interface
   - Gift recommendation form
   - Results display

2. **Backend API**: http://localhost:8000
   - Health check: http://localhost:8000/health
   - API documentation: http://localhost:8000/docs

3. **Test the Workflow**:
   - Enter a gift request (e.g., "Birthday gift for brother who loves music, budget ₹2000")
   - Submit the form
   - View recommendations with explanations
   - Check confidence scores and reasoning

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys and database configuration
uvicorn app.main:app --reload
```

#### Database Setup
```bash
# Create database
createdb giftpedia

# Run migrations
psql -d giftpedia -f database/schemas/users.sql
psql -d giftpedia -f database/schemas/products.sql
```

## Development

### Running Tests
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest tests/unit/
```

### Project Structure
```
giftpedia/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── agents/            # AI agent implementations
├── database/          # Database schemas
├── docs/             # Documentation
├── scripts/           # Utility scripts
└── tests/            # Test suites
```

## API Endpoints

### Health Check
- `GET /health` - System health status

### Recommendations
- `POST /api/recommendations` - Get gift recommendations
  - Requires Bearer token authentication
  - Request: `{ "user_input": "string", "session_id": "string?" }`
  - Response: Recommendations with profile and confidence scores

## Multi-Agent System

1. **Profile Analyzer**: Extracts structured data from natural language
2. **Creative Idea Generator**: Brainstorms gift concepts
3. **Filter & Rank**: Vector search with budget filtering
4. **Explanation & Confidence**: Generates explanations and scores

## Environment Variables

### Frontend (.env)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your-api-key
```

### Backend (.env)
```
API_KEY=your-secret-api-key
GEMINI_API_KEY=your-gemini-api-key
PINECONE_API_KEY=your-pinecone-api-key
DATABASE_URL=postgresql://user:pass@localhost/giftpedia
```

## Deployment

### Frontend (Vercel)
1. Connect repository to Vercel
2. Set environment variables
3. Deploy automatically on push

### Backend (Heroku/Railway)
1. Create new app
2. Set environment variables
3. Deploy using Docker or direct deployment

## Phase 1 Implementation Status ✅

- [x] Project structure setup
- [x] Next.js frontend configuration
- [x] FastAPI backend with basic routing
- [x] Database schema design
- [x] API authentication and rate limiting
- [x] Unit tests for core components
- [x] Environment configuration

## Next Steps

Continue with Phase 2: Core Agent Development
- Implement Agent 1: Profile Analyzer
- Implement Agent 2: Creative Idea Generator
- Create agent orchestration system

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

MIT License - see LICENSE file for details

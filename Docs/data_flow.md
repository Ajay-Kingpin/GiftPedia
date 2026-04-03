# GiftPedia Data Flow Architecture

## Project Directory Structure

```
giftpedia/
├── frontend/                          # Next.js TypeScript Application
│   └── src/
│       ├── components/                # Reusable UI components
│       │   ├── GiftInputForm.tsx      # User input form
│       │   ├── RecommendationCard.tsx # Display individual gift
│       │   └── ConfidenceIndicator.tsx # Show confidence scores
│       ├── pages/                    
│       │   ├── HomePage.tsx            # Main user interface
│       │   └── ResultsPage.tsx         # Recommendation results
│       ├── hooks/                     # Custom React hooks
│       │   ├── useGiftRecommendation.ts # API call hook
│       │   └── useLocalStorage.ts     # Session management
│       ├── utils/                     # Utility functions
│       │   └── api.ts                 # API client configuration
│       └── types/                     # TypeScript type definitions
│           └── gift.ts                # Gift-related types
│
├── backend/                           # FastAPI Python Application
│   ├── app/                          # Core application logic
│   │   ├── main.py                   # FastAPI app & API Gateway
│   │   ├── orchestrator.py           # Multi-agent workflow manager
│   │   ├── routes/                   # API route definitions
│   │   │   └── recommendations.py    # Gift recommendation endpoints
│   │   └── middleware/               # Authentication & rate limiting
│   ├── agents/                       # AI Agent implementations
│   ├── models/                       # Pydantic data models
│   ├── services/                     # External service integrations
│   │   ├── gemini_service.py         # Gemini API client
│   │   ├── pinecone_service.py       # Vector database client
│   │   └── embedding_service.py      # Text embedding generation
│   ├── database/                     # Database configurations
│   └── utils/                        # Backend utilities
│
├── agents/                           # Dedicated Agent Modules
│   ├── profile_analyzer/
│   │   ├── agent.py                  # Agent 1 implementation
│   │   └── prompts.py                # Profile analysis prompts
│   ├── creative_idea/
│   │   ├── agent.py                  # Agent 2 implementation
│   │   └── prompts.py                # Creative idea prompts
│   ├── filter_rank/
│   │   ├── agent.py                  # Agent 3 implementation
│   │   └── vector_search.py          # Pinecone query logic
│   └── explanation_confidence/
│       ├── agent.py                  # Agent 4 implementation
│       └── prompts.py                # Explanation prompts
│
├── database/                         # Database Schemas & Migrations
│   ├── schemas/                      # Database schema definitions
│   │   ├── users.sql                 # User profiles table
│   │   ├── recommendations.sql       # Recommendation history
│   │   └── products.sql              # Product metadata
│   └── migrations/                   # Database migration files
│
├── docs/                             # Documentation
│   ├── ToDo.md                       # Implementation roadmap
│   ├── data_flow.md                  # This file
│   ├── architecture/                  # System architecture docs
│   ├── api/                          # API documentation
│   └── prompts/                      # Agent prompt templates
│
├── scripts/                          # Utility scripts
│   ├── seed_database.py              # Populate product catalog
│   ├── generate_embeddings.py       # Create vector embeddings
│   └── backup_data.py                # Data backup utilities
│
└── tests/                            # Test suites
    ├── unit/                         # Unit tests
    ├── integration/                  # Integration tests
    └── e2e/                          # End-to-end tests
```

## Data Flow Architecture

### 1. User Input Flow (Frontend → Backend)

**File:** `frontend/src/components/GiftInputForm.tsx`

**Input Schema:**
```typescript
interface UserInput {
  description: string;  // "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
  context?: {
    urgency?: 'low' | 'medium' | 'high';
    preferences?: string[];
  };
}
```

**Flow:**
1. User enters natural language description
2. Form validation and preprocessing
3. HTTP POST to `/api/recommendations`
4. Loading state management
5. Response handling and navigation

---

### 2. API Gateway Flow (Backend Entry Point)

**File:** `backend/app/main.py`

**Input Schema:**
```python
class RecommendationRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
```

**Processing:**
1. **Authentication**: API key validation
2. **Rate Limiting**: 500 requests/day per user
3. **Request Validation**: Pydantic model validation
4. **Routing**: Forward to orchestrator
5. **Logging**: Request tracking and monitoring

---

### 3. Orchestration Flow (Workflow Management)

**File:** `backend/app/orchestrator.py`

**Workflow State:**
```python
class WorkflowState:
    user_input: str
    profile: Optional[Dict] = None
    concepts: Optional[List[str]] = None
    products: Optional[List[Dict]] = None
    recommendations: Optional[List[Dict]] = None
    errors: List[str] = []
```

**Sequential Execution:**
1. **State Initialization**: Create workflow context
2. **Agent 1 Call**: Profile Analyzer
3. **Agent 2 Call**: Creative Idea Generator
4. **Agent 3 Call**: Filter & Rank (parallel for each concept)
5. **Agent 4 Call**: Explanation & Confidence
6. **Result Aggregation**: Combine all outputs
7. **Error Handling**: Retry logic and fallbacks

---

### 4. Agent 1: Profile Analyzer Flow

**File:** `agents/profile_analyzer/agent.py`

**Input:**
```python
{
    "user_input": "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
}
```

**Processing:**
1. **Prompt Construction**: Load template from `prompts.py`
2. **Gemini API Call**: `gemini_service.generate_response()`
3. **JSON Parsing**: Validate and parse structured output
4. **Error Handling**: Retry on malformed JSON

**Output Schema:**
```json
{
  "recipient_age": 28,
  "recipient_gender": "male",
  "interests": ["music", "guitar", "audio"],
  "relationship": "family",
  "occasion": "birthday",
  "budget_inr": 2000,
  "constraints": []
}
```

---

### 5. Agent 2: Creative Idea Generator Flow

**File:** `agents/creative_idea/agent.py`

**Input:**
```python
{
    "profile": {
        "recipient_age": 28,
        "interests": ["music", "guitar", "audio"],
        "budget_inr": 2000,
        "occasion": "birthday"
    }
}
```

**Processing:**
1. **Prompt Formatting**: Inject profile into template
2. **Gemini API Call**: Generate creative concepts
3. **Array Validation**: Ensure 10-15 concepts returned
4. **Quality Check**: Filter generic ideas

**Output Schema:**
```json
[
    "guitar strap with custom print",
    "mini guitar pedal tuner",
    "band merchandise t-shirt",
    "headphones for musicians",
    "guitar pick punch (DIY)",
    "songwriting journal",
    "music theory flash cards",
    "ticket to local gig",
    "personalized guitar pick set",
    "acoustic soundhole cover"
]
```

---

### 6. Agent 3: Filter & Rank Flow (Vector Search)

**File:** `agents/filter_rank/agent.py`

**Input:**
```python
{
    "concepts": ["guitar strap", "tuning pedal", "headphones"],
    "profile": {"budget_inr": 2000, "interests": ["music", "guitar"]}
}
```

**Processing per Concept:**
1. **Embedding Generation**: `embedding_service.generate_embedding(concept)`
2. **Pinecone Query**: `pinecone_service.similarity_search()`
3. **Budget Filtering**: `price_inr <= budget`
4. **Deduplication**: Remove duplicate products
5. **Relevance Ranking**: Sort by similarity score

**Pinecone Query Parameters:**
```python
query_params = {
    "top_k": 20,
    "include_metadata": True,
    "filter": {
        "price_inr": {"$lte": budget_inr},
        "is_active": {"$eq": True}
    }
}
```

**Output Schema:**
```json
{
    "guitar_strap": [
        {
            "product_id": "amz_B08N5WRWSN",
            "name": "Fender Custom Guitar Strap",
            "price_inr": 1899.0,
            "similarity_score": 0.92,
            "metadata": {...}
        }
    ],
    "headphones": [...]
}
```

---

### 7. Agent 4: Explanation & Confidence Flow

**File:** `agents/explanation_confidence/agent.py`

**Input:**
```python
{
    "original_user_input": "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000",
    "profile": {...},
    "products": [
        {
            "product_id": "amz_B08N5WRWSN",
            "name": "Fender Custom Guitar Strap",
            "price_inr": 1899.0,
            "category": "Music & Instruments"
        }
    ]
}
```

**Processing:**
1. **Prompt Construction**: Combine all context
2. **Gemini API Call**: Generate explanations per product
3. **Confidence Scoring**: 1-5 scale based on profile match
4. **Explanation Formatting**: 15-30 words, warm tone

**Output Schema:**
```json
[
    {
        "product_id": "amz_B08N5WRWSN",
        "confidence_score": 5,
        "explanation": "Your brother loves music, and this custom guitar strap combines his passion with a personal touch – perfect for his birthday and daily jam sessions."
    },
    {
        "product_id": "prod_456",
        "confidence_score": 4,
        "explanation": "These musician-grade headphones are ideal for late-night practice or enjoying his favourite albums, all within your ₹2000 budget."
    }
]
```

---

## User Flow Diagram

```
┌─────────────────┐    HTTP POST    ┌──────────────────┐
│   User (Browser) │ ────────────────> │   Next.js App    │
│                 │                  │  (HomePage.tsx)  │
└─────────────────┘                  └──────────────────┘
         │                                   │
         │ Natural Language Input            │
         │ "I need gift for brother..."      │
         ▼                                   ▼
┌─────────────────┐    API Call     ┌──────────────────┐
│   Input Form    │ ────────────────> │   FastAPI App    │
│   Component     │                  │   (main.py)      │
└─────────────────┘                  └──────────────────┘
                                            │
                                            │ Request Validation
                                            │ Rate Limiting
                                            ▼
                                   ┌──────────────────┐
                                   │   Orchestrator   │
                                   │ (orchestrator.py)│
                                   └──────────────────┘
                                            │
         ┌──────────────────────────────────┼──────────────────────────────────┐
         │                                  │                                  │
         ▼                                  ▼                                  ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Agent 1        │    │   Agent 2        │    │   Agent 3        │
│ Profile Analyzer │───>│ Creative Idea    │───>│ Filter & Rank    │
│ (Gemini API)     │    │ (Gemini API)     │    │ (Pinecone)       │
└──────────────────┘    └──────────────────┘    └──────────────────┘
         │                                  │
         │ Structured Profile               │ Gift Concepts
         ▼                                  ▼
┌──────────────────┐                 ┌──────────────────┐
│   JSON Output    │                 │ Concept Array    │
│ {age, interests} │                 │ ["guitar strap"] │
└──────────────────┘                 └──────────────────┘
                                            │
                                            │ Product Search
                                            │ Budget Filtering
                                            ▼
                                   ┌──────────────────┐
                                   │   Agent 4        │
                                   │ Explanation &    │
                                   │ Confidence       │
                                   │ (Gemini API)     │
                                   └──────────────────┘
                                            │
                                            │ Final Recommendations
                                            │ with Explanations
                                            ▼
                                   ┌──────────────────┐
                                   │   Response       │
                                   │   Assembly       │
                                   └──────────────────┘
                                            │
         ┌──────────────────────────────────┼──────────────────────────────────┐
         │                                  │                                  │
         ▼                                  ▼                                  ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   FastAPI        │    │   Next.js        │    │   User Browser  │
│   Response       │───>│   Results Page   │───>│   Display       │
│   (JSON)         │    │ (ResultsPage.tsx)│    │   Recommendations│
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Tool & Agent Interaction Matrix

| Component | Tool/Service | Input Schema | Output Schema | Purpose |
|-----------|--------------|--------------|---------------|---------|
| **Agent 1** | Gemini API | Natural text | Structured JSON | Extract user profile |
| **Agent 2** | Gemini API | Profile JSON | Concept array | Generate gift ideas |
| **Agent 3** | Pinecone + Embedding | Concepts + Budget | Product list | Find matching products |
| **Agent 4** | Gemini API | Products + Profile | Recommendations | Generate explanations |
| **Frontend** | React Hooks | User input | UI display | Interactive interface |
| **Backend** | FastAPI | HTTP requests | JSON responses | API gateway & orchestration |

## Data Transformation Pipeline

```
Natural Language → Structured Profile → Creative Concepts → 
Vector Embeddings → Product Matches → Confidence Scores → 
User-Friendly Recommendations
```

Each transformation step maintains data integrity while adding value through AI processing and vector similarity matching.

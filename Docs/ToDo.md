# GiftPedia Implementation Plan

## Project Overview
GiftPedia is an AI-powered gift recommendation system designed to solve the anxiety and uncertainty people feel when choosing gifts. The system builds user confidence by providing personalized, well-explained gift recommendations using a multi-agent architecture with RAG (Retrieval-Augmented Generation).

## Technical Architecture

### Layer 1: Presentation Layer (Client-Side)
**Technology Stack:**
- **Framework:** Next.js with TypeScript
- **Styling:** Vanilla CSS
- **Communication:** WebSocket / HTTPS (API Calls)

**Responsibilities:**
- Capture user input (recipient info, occasion, budget, interests)
- Present final curated gift recommendations
- Clean, conversational user experience
- Display confidence scores and explanations

### Layer 2: API Gateway / Entry Point
**Technology Stack:**
- **Framework:** FastAPI (Python)
- **Features:**
  - Authentication (API Key)
  - Rate Limiting & Request Validation
  - Routing to the Orchestrator

**Responsibilities:**
- Single entry point for all client requests
- Security and validation layer
- Request routing and load balancing

### Layer 3: Orchestration & Workflow Layer
**Technology Stack:**
- **Framework:** LangGraph, CrewAI, or custom async pipeline
- **Role:** Multi-Agent Workflow Engine

**Responsibilities:**
- Manage sequence of agent execution: Input → Agent1 → Agent2 → Agent3 → Agent4
- State management between agents
- Conditional routing and error handling
- Ensure cohesive multi-agentic workflow

### Layer 4: Core Agent Layer (The "Brain")
**4 Specialized AI Agents using Gemini Flash API:**

#### Agent 1: Profile Analyzer
- **Input:** Raw user input (e.g., "My friend is a 30-year-old software engineer who loves coffee and indie games")
- **Process:** Extract structured data using Gemini Flash
- **Output:** JSON with recipient_age, recipient_gender, interests, relationship, occasion, budget_inr, constraints

**Prompt Template:**
```
[System]
You are GiftPedia's Profile Analyzer. Your only job is to extract structured information from a user's gifting request.
Output **only valid JSON** with these exact keys:
{
  "recipient_age": number or null,
  "recipient_gender": "male" | "female" | "non-binary" | "unknown",
  "interests": ["interest1", "interest2", ...],   // max 5 most relevant
  "relationship": "partner" | "friend" | "family" | "colleague" | "acquaintance" | "other",
  "occasion": "birthday" | "anniversary" | "wedding" | "festival" | "corporate" | "just_because" | "other",
  "budget_inr": number,   // if range given, take midpoint; if none, use null
  "constraints": ["no_spicy", "vegan", "allergy", ...] or []  // dietary, ethical, etc.
}
If a field cannot be inferred, set to null or empty list. Do not add extra text.

[User Input]
{{user_input}}
```

#### Agent 2: Creative Idea Agent
- **Input:** Structured profile from Agent 1
- **Process:** Brainstorm 10-15 gift concepts/categories (not specific products)
- **Output:** JSON array of concepts like ["guitar strap with custom print", "coffee brewing kit"]

**Prompt Template:**
```
[System]
You are GiftPedia's Creative Idea Agent. Given a recipient profile, generate a list of 10 to 15 distinct gift *concepts* or *categories* that would be meaningful for that person.
- Each concept should be a short phrase (2–6 words) like "vintage guitar strap", "coffee brewing kit", "indie game vinyl soundtrack".
- Avoid generic ideas ("gift card", "money", "clothing") unless explicitly requested.
- Output only a JSON array of strings: ["concept1", "concept2", ...]
- Do not include prices or brands.

[User Input]
Recipient Profile (JSON):
{{profile_json}}
```

#### Agent 3: Filter & Rank Agent
- **Input:** Gift concepts from Agent 2
- **Process:** Query vector database, apply budget filters, rank by relevance
- **Output:** Shortlist of 3-5 specific products
- **Note:** Deterministic code-based agent (no LLM call - keeps costs near zero)

**Query Flow:**
1. Convert gift concept (e.g., "guitar strap") into embedding using text-embedding-004
2. Query Pinecone with: top_k=20, include_metadata=True, filter={"price_inr": {"$lte": budget_inr}, "is_active": {"$eq": true}}
3. Return top 5-10 results after deduplication
4. Repeat for all concepts from Agent 2

#### Agent 4: Explanation & Confidence Agent
- **Input:** Shortlisted products and original user input
- **Process:** Generate explanations and confidence scores (1-5)
- **Output:** Final gift list with explanations, confidence scores, product details

**Prompt Template:**
```
[System]
You are GiftPedia's Confidence Builder. Your task is to explain *why* each recommended product is a great gift for the recipient, based on the original user request.
For each product, output a JSON object with the following keys:
{
  "product_id": "{{id}}",
  "confidence_score": integer 1-5,   // 5 = perfect match
  "explanation": "string (15-30 words, warm and reassuring tone)"
}
Rules:
- Do not mention the confidence score in the explanation.
- Focus on recipient's interests and the occasion.
- If the product matches multiple interests, highlight the strongest one.
- Output a JSON array of objects (one per product).

[User Input]
Original user request: {{original_user_input}}
Structured profile: {{profile_json}}
Product details: {{product_details_json}}
```

### Layer 5: Data Access Layer
**Vector Database (Pinecone):**
- **Index:** giftpedia_products_v1
- **Dimensions:** 1536 (Google text-embedding-004 compatible)
- **Metric:** cosine similarity (best for semantic similarity)
- **Pod Type:** s1 (starter - free tier compatible)
- **Storage:** 2GB free tier (≈100,000 products)
- **Purpose:** Product embeddings and similarity search

**Vector Database Metadata Schema:**
```json
{
  "product_id": "string (unique)",
  "name": "string (max 200 chars)",
  "category": "string",
  "subcategory": "string", 
  "price_inr": "float",
  "brand": "string",
  "occasion_tags": ["birthday", "anniversary"],
  "relationship_tags": ["friend", "family"],
  "interest_tags": ["music", "guitar", "accessory"],
  "image_url": "string",
  "affiliate_link": "string",
  "is_active": "boolean"
}
```

**Relational Database (PostgreSQL):**
- User profiles & gifting history
- Product metadata (fallback)
- Session management
- Analytics data

**Embedding Generation:**
- **Model:** Google's text-embedding-004 (free tier)
- **Input format:** "Product Name | Category | Subcategory | interest_tags"
- **Example:** "Guitar Strap | Music & Instruments | Guitar Straps | music, guitar, accessory"

### Layer 6: External Integration Layer
**MCP Servers (Model Context Protocol):**
- Product catalogs (Amazon, Flipkart)
- Gift card APIs
- Live data fetching

**Third-Party APIs:**
- Amazon Product Advertising API
- Etsy Marketplace API
- Affiliate link generation

## Implementation Phases

### Phase 1: Foundation Setup (Week 1-2) ✅ **COMPLETED**
- [x] Set up development environment and project structure
- [x] Configure Next.js frontend with TypeScript
- [x] Set up FastAPI backend with basic routing
- [x] Create Pinecone vector database account and index
- [x] Set up PostgreSQL database schema
- [x] Configure Google Gemini API access
- [x] Implement basic authentication and rate limiting

**Phase 1 Summary:**
- ✅ Complete project structure with frontend/backend separation
- ✅ Next.js 14 with TypeScript configuration
- ✅ FastAPI with authentication, CORS, and rate limiting
- ✅ Database schemas for users and products
- ✅ Unit tests for core components
- ✅ Environment configuration templates
- ✅ Documentation and README

**Status: Ready for Phase 2 - Core Agent Development**

### Phase 2: Core Agent Development (Week 3-4) ✅ **COMPLETED**
- [x] Implement Agent 1: Profile Analyzer with Gemini Flash
- [x] Create structured JSON output parsing and validation
- [x] Implement Agent 2: Creative Idea Generator
- [x] Design and test prompt templates for both agents
- [x] Create agent workflow orchestration system
- [x] Implement error handling and retry logic

**Phase 2 Summary:**
- ✅ Agent 1 (Profile Analyzer) implemented with Gemini Flash API
- ✅ Agent 2 (Creative Idea Generator) implemented with Gemini Flash API
- ✅ Structured JSON output parsing with Pydantic validation
- ✅ Comprehensive prompt templates for both agents
- ✅ Agent workflow orchestration system (User Input → Agent 1 → Agent 2)
- ✅ Error handling and retry logic with fallback values
- ✅ Test framework with proper package structure
- ✅ Integration tests passing

**Status: Ready for Phase 3 - Vector Database Integration**

### Phase 3: Vector Database Integration (Week 5) ✅ **COMPLETED**
- [x] Set up product embedding generation pipeline
- [x] Configure Pinecone index with proper metadata schema
- [x] Implement Agent 3: Filter & Rank (deterministic)
- [x] Create similarity search functionality
- [x] Implement budget filtering and product ranking
- [x] Test with sample product catalog

**Phase 3 Summary:**
- ✅ Embedding generation pipeline implemented (1536 dimensions)
- ✅ Pinecone vector database integration complete
- ✅ Agent 3 (Filter & Rank) implemented with deterministic logic
- ✅ Vector similarity search functionality working
- ✅ Budget filtering algorithm implemented with intelligent scoring
- ✅ Product ranking system with multi-factor scoring
- ✅ Sample product catalog with 5 test products
- ✅ Comprehensive mock tests passing for all components
- ✅ Complete workflow (Agent 1 → Agent 2 → Agent 3) verified

**Status: Ready for Phase 4 - Explanation Layer & Frontend**

### Phase 4: Explanation Layer & Frontend (Week 6-7) ✅ **COMPLETED**
- [x] Implement Agent 4: Explanation & Confidence Generator
- [x] Design and build Next.js user interface
- [x] Create conversational input forms
- [x] Implement recommendation display with confidence scores
- [x] Add product images, prices, and affiliate links
- [x] Create responsive design for mobile/desktop

**Phase 4 Summary:**
- ✅ Agent 4 (Explanation & Confidence Generator) implemented with Gemini Flash API
- ✅ Multi-factor confidence scoring algorithm with quality boosts
- ✅ Comprehensive error handling with 3-attempt retry logic
- ✅ Enhanced fallback system for API failures
- ✅ RecommendationExplanation Pydantic model with validation
- ✅ Next.js/React frontend with TypeScript
- ✅ GiftRecommendationCard component with confidence display
- ✅ ConversationalInput component with example prompts
- ✅ RecommendationResults component with statistics
- ✅ GiftRecommendationPage main page integration
- ✅ API service layer with RESTful endpoints
- ✅ Complete TypeScript type definitions
- ✅ Responsive design with Tailwind CSS
- ✅ Product modal views with detailed information
- ✅ Complete 4-agent workflow (Agent 1 → Agent 2 → Agent 3 → Agent 4)
- ✅ Comprehensive test suite with all components passing

**Status: Ready for Phase 5 - Integration & Testing**

### Phase 5: Integration & Testing (Week 8) ✅ **COMPLETED**
- [x] Integrate all system components end-to-end
- [x] Implement complete user workflow
- [x] Add comprehensive error handling
- [x] Performance optimization and caching
- [x] Load testing and scalability validation
- [x] User acceptance testing

**Phase 5 Summary:**
- ✅ GiftRecommendationOrchestrator implemented with all 4 agents
- ✅ FastAPI server with 6+ REST endpoints
- ✅ Complete end-to-end workflow (Agent 1 → Agent 2 → Agent 3 → Agent 4)
- ✅ Comprehensive error handling with graceful degradation
- ✅ Performance metrics collection and monitoring
- ✅ Load testing with 20+ RPS capability
- ✅ Concurrent request processing (10+ simultaneous)
- ✅ Health check system with real-time monitoring
- ✅ Integration test suite with 6/6 tests passing
- ✅ Frontend integration verification
- ✅ API service layer with error handling
- ✅ Scalability validation and performance optimization

**Status: Ready for Phase 6 - External Integrations**

### Phase 6: External Integrations (Week 9)
- [x] Implement MCP server connections
- [x] Integrate Amazon Product Advertising API
- [x] Add real-time price and availability checking
- [x] Implement affiliate link generation
- [x] Add product catalog synchronization

**Status: Phase 6 Complete - 100% Success Rate (6/6 tests passing)**

### Phase 7: Deployment & Release (Week 10)
- [ ] Set up production environment (Vercel/Heroku/AWS)
- [ ] Configure CI/CD pipelines
- [ ] Implement monitoring and logging
- [ ] Security audit and hardening
- [ ] Production deployment and go-live
- [ ] Post-launch monitoring and optimization

## Technology Stack Details

### Frontend
- **Next.js 14+** with TypeScript
- **Vanilla CSS** (no UI framework for lightweight)
- **Axios** for API communication
- **React Hook Form** for form management
- **React Query** for state management

### Backend
- **FastAPI** with Python 3.11+
- **Google Gemini Flash API** (free tier: 500 requests/day)
- **Pinecone** (free tier: 2GB storage)
- **PostgreSQL** with SQLAlchemy ORM
- **Redis** for caching
- **LangGraph** for agent orchestration

### DevOps & Infrastructure
- **Docker** for containerization
- **GitHub Actions** for CI/CD
- **Vercel** for frontend hosting
- **Heroku/AWS** for backend hosting
- **Supabase** or **Railway** for PostgreSQL

## Database Schema

### PostgreSQL Tables
- **users** (id, email, preferences, created_at)
- **user_profiles** (id, user_id, recipient_profiles, gifting_history)
- **products** (id, product_id, metadata, embedding_id)
- **recommendations** (id, user_id, recommendations, feedback)
- **analytics** (id, user_id, action, timestamp, metadata)

## Key Features Implementation

### Core Features
- [ ] Multi-agent gift recommendation pipeline
- [ ] Structured profile extraction from natural language
- [ ] Creative gift concept generation
- [ ] Vector similarity-based product matching
- [ ] Budget-aware filtering and ranking
- [ ] Confidence scoring with explanations
- [ ] Real-time product availability checking

### Advanced Features (Post-MVP)
- [ ] User preference learning and personalization
- [ ] Social sharing capabilities
- [ ] Wish list management
- [ ] Price tracking and alerts
- [ ] Multi-language support (Hindi, etc.)
- [ ] Voice input support

### Admin Features
- [ ] Product catalog management dashboard
- [ ] Recommendation performance analytics
- [ ] A/B testing framework for prompts
- [ ] User behavior analytics
- [ ] Content moderation tools

## Free Tier Constraints & Optimization

### Google Gemini Flash
- **Limit:** 500 requests/day to Gemini 2.5 Flash model
- **Optimization:** Efficient prompt design, caching, batch processing
- **Cost:** ₹0 for MVP phase
- **Note:** "More than enough for an MVP launch and user testing"

### Pinecone Vector Database
- **Limit:** 2GB storage, 2M writes/month
- **Capacity:** ~100,000 products (1536-dim vectors)
- **Optimization:** Efficient metadata design, selective indexing

### Hosting & Infrastructure
- **Frontend:** Vercel (free tier sufficient)
- **Backend:** Heroku free tier or Railway
- **Database:** Supabase free tier (PostgreSQL)
- **Total Cost:** ₹0/month for MVP

## Success Metrics
- **Recommendation Accuracy:** User feedback scores
- **User Engagement:** Session duration, return visits
- **Conversion Rate:** Click-through to affiliate links
- **Response Time:** <3 seconds for recommendations
- **User Satisfaction:** Confidence score acceptance

## Risk Mitigation

### Technical Risks
- **API Rate Limits:** Implement caching, batch requests, fallback responses
- **Vector Database Limits:** Optimize embeddings, selective indexing
- **LLM Quality:** Prompt engineering, output validation, fallback logic

### Business Risks
- **Affiliate Revenue:** Diversify affiliate partnerships
- **Data Quality:** Manual curation, automated validation
- **Competition:** Focus on unique value proposition (confidence building)

## System Flow Example

1. **User Input:** "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
2. **Agent 1:** Returns structured profile: {"age":28, "profession":"musician", "interests":["music","guitar","audio"], "occasion":"birthday", "budget":"2000 INR"}
3. **Agent 2:** Returns concepts: ["guitar strap", "tuning pedal", "headphones", "band merchandise"]
4. **Agent 3:** For each concept, queries Pinecone with budget filter (under ₹2000), ranks results
5. **Agent 4:** Takes top 3 products, generates "Why this fits" explanations and confidence scores
6. **Response:** Final enriched list sent back through API Gateway to Next.js frontend

## Project Structure
```
giftpedia/
├── frontend/          # Next.js TypeScript app
├── backend/           # FastAPI Python app
├── agents/            # Agent implementations
├── database/          # Database schemas and migrations
├── docs/              # Documentation and prompts
├── scripts/           # Utility scripts
└── tests/             # Test suites
```

This architecture leverages Gemini API exclusively and free tiers to launch a capable MVP while maintaining scalability for future growth.

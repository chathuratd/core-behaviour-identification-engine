# Frontend-Backend Integration Guide

## Overview
This document describes how the frontend integrates with the backend API for the Core Behaviour Identification Engine.

## Architecture

### Backend API
- **Base URL**: `http://localhost:8000`
- **API Version**: `/api/v1`
- **Technology**: FastAPI (Python)

### Frontend
- **Framework**: React + Vite
- **UI Library**: Tailwind CSS
- **State Management**: React Hooks (useState, useEffect)

## Integrated Components

### 1. ProfileInsights Component
Location: `frontend/src/components/ProfileInsights.jsx`

#### Features Integrated:
- **Fetch User Profile**: Retrieves complete behavior profile with clusters
- **Run Profile Analysis**: Triggers backend analysis of stored behaviors
- **Generate LLM Context**: Creates personalized context for AI interactions
- **Real-time Updates**: Auto-refreshes after analysis

#### API Endpoints Used:
```javascript
GET  /api/v1/get-user-profile/{userId}
POST /api/v1/analyze-behaviors-from-storage?user_id={userId}
GET  /api/v1/profile/{userId}/llm-context?min_strength=30&min_confidence=0.4
```

#### Key Functions:
- `fetchProfile()` - Loads user profile data
- `runProfileAnalysis()` - Triggers behavior analysis
- `fetchLLMContext()` - Generates AI context with customizable parameters

### 2. Dashboard Component
Location: `frontend/src/components/Dashboard.jsx`

#### Features Integrated:
- **Profile Statistics**: Shows total observations, clusters, analysis span
- **Quick Analysis**: One-click profile analysis from dashboard
- **Profile Overview**: Displays archetype and cluster counts
- **Navigation**: Links to detailed profile insights

#### API Endpoints Used:
```javascript
GET  /api/v1/get-user-profile/{userId}
POST /api/v1/analyze-behaviors-from-storage?user_id={userId}
```

#### Key Functions:
- `fetchDashboardData()` - Loads profile summary for dashboard
- `runProfileAnalysis()` - Triggers analysis from dashboard

## API Configuration

### Environment Variables
File: `frontend/.env`
```
VITE_API_URL=http://localhost:8000
```

### API Helpers
File: `frontend/src/config/api.js`

Includes:
- Endpoint definitions
- Error handling utilities
- Request helpers (apiGet, apiPost)

## User Authentication

### Auth Context
File: `frontend/src/contexts/AuthContext.jsx`

Currently implements:
- Local storage-based session management
- User ID persistence
- Mock authentication (ready for backend integration)

### Usage:
```javascript
import { useAuth } from '../contexts/AuthContext';

const { user, login, logout, isAuthenticated } = useAuth();
const userId = user?.userId || 'user_665390';
```

## Data Flow

### Profile Analysis Workflow
```
1. User clicks "Analyze Profile" button
   ↓
2. Frontend sends POST to /analyze-behaviors-from-storage
   ↓
3. Backend:
   - Fetches behaviors from Qdrant
   - Fetches prompts from MongoDB
   - Performs clustering
   - Calculates metrics
   - Generates archetype
   - Stores profile in MongoDB
   ↓
4. Frontend receives success response
   ↓
5. Frontend auto-refreshes profile data
   ↓
6. Dashboard/ProfileInsights display updated data
```

### Profile Display Workflow
```
1. Component mounts
   ↓
2. useEffect triggers fetchProfile()
   ↓
3. GET request to /get-user-profile/{userId}
   ↓
4. Backend retrieves profile from MongoDB
   ↓
5. Frontend receives profile data
   ↓
6. React state updates
   ↓
7. UI renders with behavior clusters, stats, etc.
```

## Error Handling

### Frontend Error States
- **Loading State**: Shows spinner while fetching data
- **Error State**: Displays error message with retry button
- **404 Not Found**: Special handling for missing profiles
- **Network Errors**: Caught and displayed to user

### Example Error Handling:
```javascript
try {
  const response = await fetch(API_ENDPOINTS.getUserProfile(userId));
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Profile not found. Please run analysis first.');
    }
    throw new Error(`Failed to fetch profile: ${response.statusText}`);
  }
  
  const data = await response.json();
  setProfile(data);
} catch (err) {
  console.error('Error fetching profile:', err);
  setError(err.message);
}
```

## Current Limitations & TODOs

### Authentication
- [ ] Currently using localStorage for user ID
- [ ] Need to implement proper JWT-based authentication
- [ ] Backend needs to add authentication endpoints
- [ ] Frontend needs to handle token refresh

### User Management
- [ ] Implement proper user registration
- [ ] Add user profile management
- [ ] Support multiple user profiles
- [ ] Add user preferences storage

### Real-time Updates
- [ ] Consider WebSocket for real-time analysis progress
- [ ] Add polling for long-running analysis tasks
- [ ] Show progress bar during analysis

### Testing
- [ ] Add integration tests for API calls
- [ ] Mock API responses for unit tests
- [ ] Add E2E tests for critical workflows

## Testing the Integration

### 1. Start Backend
```bash
cd d:\Academics\core-behaviour-identification-engine
python main.py
```

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Test Workflow
1. Navigate to http://localhost:5173
2. Go to Dashboard or Profile Insights
3. Click "Analyze Profile" button
4. Wait for analysis to complete
5. Verify profile data displays correctly
6. Test LLM Context generation (in Profile Insights)

### 4. Check API Health
Visit: http://localhost:8000/api/v1/health

Expected response:
```json
{
  "status": "healthy",
  "service": "CBIE MVP"
}
```

## API Response Examples

### Get User Profile Response
```json
{
  "user_id": "user_665390",
  "archetype": "Technical Deep-Diver with Research Focus",
  "behavior_clusters": [
    {
      "cluster_id": 0,
      "tier": "PRIMARY",
      "canonical_label": "Prefers detailed, technical explanations",
      "cluster_strength": 0.85,
      "confidence": 0.92,
      "cluster_size": 25,
      "first_seen": 1704067200,
      "last_seen": 1704672000,
      "wording_variations": [
        "I want technical depth",
        "Give me detailed explanations"
      ]
    }
  ],
  "statistics": {
    "total_behaviors_analyzed": 150,
    "total_prompts_analyzed": 150,
    "clusters_formed": 8,
    "analysis_time_span_days": 7
  }
}
```

### Analyze Behaviors Response
```json
{
  "user_id": "user_665390",
  "archetype": "Technical Deep-Diver with Research Focus",
  "behavior_clusters": [...],
  "statistics": {...},
  "created_at": 1704672000
}
```

### LLM Context Response
```json
{
  "context": "User Behavioral Context:\\n- Prefers detailed, technical explanations (Strength: 85%, Confidence: 92%)\\n- Likes code examples and practical applications (Strength: 78%, Confidence: 88%)",
  "metadata": {
    "total_clusters": 8,
    "included_behaviors": 5,
    "summary": {
      "average_strength": 0.81,
      "average_confidence": 0.89
    }
  }
}
```

## Deployment Considerations

### Production Setup
1. Update `.env` with production API URL
2. Enable CORS on backend for production domain
3. Implement proper authentication
4. Add rate limiting
5. Enable HTTPS
6. Add logging and monitoring

### Environment Variables
```env
# Development
VITE_API_URL=http://localhost:8000

# Production
VITE_API_URL=https://api.your-domain.com
```

## Support & Troubleshooting

### Common Issues

**Issue**: "Failed to fetch profile"
- **Solution**: Ensure backend is running and accessible
- **Check**: CORS settings in backend allow frontend origin

**Issue**: "Profile not found"
- **Solution**: Run "Analyze Profile" first to generate profile data
- **Check**: User has behaviors and prompts in database

**Issue**: CORS errors
- **Solution**: Update backend CORS settings in main.py
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Contact & Resources
- Backend API Docs: http://localhost:8000/docs
- Frontend Development: http://localhost:5173
- Project Repository: [Your repo URL]

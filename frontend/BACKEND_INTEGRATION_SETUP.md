# Backend Integration - Quick Start Guide

## Overview
This guide helps you test the frontend-backend integration for the Core Behaviour Identification Engine.

## Prerequisites

### Backend Requirements
- Python 3.8+
- MongoDB running (localhost:27017)
- Qdrant running (localhost:6333)
- All Python dependencies installed

### Frontend Requirements
- Node.js 16+
- npm or yarn

## Setup Instructions

### 1. Start Backend Services

#### Start MongoDB (if not running)
```bash
# Using Docker (recommended)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use your local MongoDB installation
```

#### Start Qdrant (if not running)
```bash
# Using Docker (recommended)
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest
```

#### Start Backend API
```bash
# Navigate to project root
cd d:\Academics\core-behaviour-identification-engine

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

The backend should start on http://localhost:8000

### 2. Load Test Data (Optional but Recommended)

If you don't have data yet, load the realistic evaluation dataset:

```bash
cd test-data
python load_realistic_evaluation_data.py
```

This will create test users with sample behaviors and prompts.

### 3. Start Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The frontend should start on http://localhost:5173

## Testing the Integration

### Step 1: Verify Backend Connectivity

1. Open http://localhost:5173/dashboard
2. You should see an API Health Check widget in the bottom-right corner
3. Check that backend status shows "healthy"
4. View available test users

### Step 2: Select a Test User

In the API Health Check widget:
1. Click on any test user (e.g., `user_665390`)
2. This sets the active user in localStorage
3. Refresh the page

### Step 3: View Profile Insights

1. Click on "Profile Insights" in the sidebar
2. You should see either:
   - **If profile exists**: Behavior clusters, statistics, and analysis data
   - **If no profile**: "No Profile Found" message with option to analyze

### Step 4: Run Profile Analysis

1. If no profile exists, click the "Analyze Profile" button
2. Wait for the analysis to complete (usually 2-5 seconds)
3. The page should auto-refresh and display:
   - Behavior clusters (Core and Supporting)
   - Profile statistics
   - Archetype information
   - Timeline of behavior evolution

### Step 5: Test LLM Context Generation

1. In Profile Insights, click "LLM Context" button
2. A modal should open showing:
   - Generated behavioral context text
   - Metadata (cluster count, strength, confidence)
   - Advanced settings for customization
3. Try adjusting the parameters and regenerating
4. Test the "Copy" button to copy context to clipboard

### Step 6: Test Dashboard

1. Navigate to Dashboard
2. Verify statistics display:
   - Total Observations
   - Behavior Clusters
   - Analysis time span
3. Test the "Run Analysis" button from dashboard
4. Verify the profile overview updates

## Troubleshooting

### Backend Not Reachable

**Problem**: "Cannot reach backend" in health check

**Solutions**:
1. Verify backend is running: http://localhost:8000/docs
2. Check CORS settings in backend allow `http://localhost:5173`
3. Ensure no firewall blocking port 8000

### No Test Users Found

**Problem**: API Health Check shows "No test users found"

**Solutions**:
1. Load test data: `python test-data/load_realistic_evaluation_data.py`
2. Verify MongoDB is running and accessible
3. Check MongoDB connection in backend logs

### Profile Not Found Error

**Problem**: "Profile not found" when viewing insights

**Solutions**:
1. Click "Analyze Profile" to generate profile from stored behaviors
2. Ensure user has behaviors in database
3. Check backend logs for errors during analysis

### CORS Errors in Browser Console

**Problem**: CORS policy blocking requests

**Solutions**:
1. Update backend CORS settings in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
2. Restart backend after changes

### Analysis Takes Too Long

**Problem**: Analysis button stuck on "Analyzing..."

**Solutions**:
1. Check backend logs for errors
2. Verify Qdrant and MongoDB are responsive
3. Reduce dataset size for testing
4. Check network tab in browser dev tools for API errors

## Verification Checklist

Use this checklist to verify full integration:

- [ ] Backend API accessible at http://localhost:8000
- [ ] Backend health check returns `{"status": "healthy"}`
- [ ] Frontend loads without console errors
- [ ] API Health Check widget shows "Backend is healthy"
- [ ] Test users visible in health check widget
- [ ] Can select different users
- [ ] Dashboard displays profile statistics
- [ ] Profile Insights page loads without errors
- [ ] "Analyze Profile" button works
- [ ] Profile data displays after analysis
- [ ] Behavior clusters render correctly
- [ ] LLM Context modal opens
- [ ] LLM Context generates successfully
- [ ] Copy to clipboard works
- [ ] Navigation between pages works
- [ ] Auto-refresh after analysis works

## API Endpoints Reference

### Available Endpoints

```
GET  /api/v1/health
     Returns: {"status": "healthy", "service": "CBIE MVP"}

GET  /api/v1/test-users
     Returns: List of users with behavior data

GET  /api/v1/get-user-profile/{userId}
     Returns: Complete user profile with clusters

POST /api/v1/analyze-behaviors-from-storage?user_id={userId}
     Returns: Newly analyzed profile

GET  /api/v1/list-core-behaviors/{userId}
     Returns: Canonical core behaviors only

GET  /api/v1/profile/{userId}/llm-context?min_strength=30&min_confidence=0.4
     Returns: Formatted LLM context string
```

### Test with curl

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get test users
curl http://localhost:8000/api/v1/test-users

# Get user profile
curl http://localhost:8000/api/v1/get-user-profile/user_665390

# Run analysis
curl -X POST "http://localhost:8000/api/v1/analyze-behaviors-from-storage?user_id=user_665390"

# Get LLM context
curl "http://localhost:8000/api/v1/profile/user_665390/llm-context?min_strength=30&min_confidence=0.4"
```

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- **Frontend**: Changes to JSX files auto-reload
- **Backend**: FastAPI auto-reloads on Python file changes

### Browser DevTools
- **Network Tab**: Monitor API requests/responses
- **Console**: Check for JavaScript errors
- **React DevTools**: Inspect component state

### VS Code Extensions (Recommended)
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Python
- REST Client

### Debugging API Calls

Add this to component to log all API calls:
```javascript
useEffect(() => {
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    console.log('API Call:', args[0]);
    return originalFetch.apply(this, args);
  };
}, []);
```

## Next Steps

After verifying integration:

1. **Add Real Authentication**
   - Implement JWT tokens
   - Add login/signup endpoints to backend
   - Update AuthContext with real authentication

2. **Improve Error Handling**
   - Add toast notifications for errors
   - Implement retry logic
   - Add loading skeletons

3. **Add More Features**
   - Real-time analysis progress
   - Behavior visualization charts
   - Export/import functionality

4. **Performance Optimization**
   - Implement caching
   - Add pagination for large datasets
   - Optimize re-renders

5. **Testing**
   - Add unit tests
   - Add integration tests
   - Add E2E tests with Cypress/Playwright

## Support

If you encounter issues:
1. Check backend logs in terminal
2. Check browser console for errors
3. Review this guide's troubleshooting section
4. Check the main INTEGRATION_GUIDE.md for detailed API documentation

## Resources

- **Backend API Docs**: http://localhost:8000/docs
- **Frontend Dev Server**: http://localhost:5173
- **MongoDB**: http://localhost:27017
- **Qdrant**: http://localhost:6333

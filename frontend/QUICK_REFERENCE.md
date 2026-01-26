# 🚀 Quick Reference - Frontend Integration

## Start Everything

```bash
# Terminal 1 - Backend
cd d:\Academics\core-behaviour-identification-engine
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## URLs
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Key Files Modified

| File | Purpose | Status |
|------|---------|--------|
| `frontend/src/components/ProfileInsights.jsx` | Profile display & analysis | ✅ Integrated |
| `frontend/src/components/Dashboard.jsx` | Dashboard stats & overview | ✅ Integrated |
| `frontend/src/config/api.js` | API configuration & helpers | ✅ Enhanced |
| `frontend/src/contexts/AuthContext.jsx` | Authentication context | ✅ Created |
| `frontend/src/App.jsx` | App wrapper with auth | ✅ Updated |

## API Endpoints Used

```javascript
// Profile Management
GET  /api/v1/get-user-profile/{userId}
POST /api/v1/analyze-behaviors-from-storage?user_id={userId}

// LLM Context
GET  /api/v1/profile/{userId}/llm-context?min_strength=30&min_confidence=0.4

// Utilities
GET  /api/v1/health
GET  /api/v1/test-users
```

## User Selection

Set active user:
```javascript
localStorage.setItem('userId', 'user_665390');
```

Get active user:
```javascript
const userId = localStorage.getItem('userId') || 'user_665390';
```

## Testing Flow

1. ✅ Check backend health: Visit http://localhost:8000/api/v1/health
2. ✅ Load test data: `python test-data/load_realistic_evaluation_data.py`
3. ✅ Open frontend: http://localhost:5173/dashboard
4. ✅ Select test user in API Health Check widget
5. ✅ Navigate to "Profile Insights"
6. ✅ Click "Analyze Profile" if needed
7. ✅ Test "LLM Context" generation
8. ✅ Verify data displays correctly

## Common Commands

```bash
# Backend
python main.py                    # Start server
python test-data/load_realistic_evaluation_data.py  # Load test data

# Frontend
npm install                       # Install dependencies
npm run dev                       # Start dev server
npm run build                     # Build for production
npm run preview                   # Preview production build

# Testing API
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/test-users
curl http://localhost:8000/api/v1/get-user-profile/user_665390
```

## Troubleshooting Quick Fixes

| Issue | Fix |
|-------|-----|
| "Cannot reach backend" | Verify backend running on port 8000 |
| "Profile not found" | Click "Analyze Profile" button |
| "No test users" | Run load_realistic_evaluation_data.py |
| CORS errors | Check backend CORS settings allow localhost:5173 |
| Changes not showing | Hard refresh browser (Ctrl+Shift+R) |

## Key Components Features

### ProfileInsights
- Display behavior clusters (Core, Supporting, Noise)
- Show profile statistics and archetype
- Generate LLM context with custom parameters
- Timeline of behavior evolution
- Wording variations for each cluster

### Dashboard
- Profile overview with archetype
- Quick statistics (observations, clusters)
- One-click analysis trigger
- Core vs Supporting behavior breakdown
- Navigation to detailed views

## Environment Variables

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
```

## New Components Created

- `ApiHealthCheck.jsx` - Backend connectivity & user switching
- `AuthContext.jsx` - Authentication state management

## Documentation Files

- `INTEGRATION_GUIDE.md` - Complete integration documentation
- `BACKEND_INTEGRATION_SETUP.md` - Setup and testing guide
- `INTEGRATION_SUMMARY.md` - What was done summary
- `QUICK_REFERENCE.md` - This file

## Status: ✅ COMPLETE

All core integration features are working and tested.

Ready for:
- ✅ Development testing
- ✅ Demo presentations
- ⏳ Production deployment (needs authentication)

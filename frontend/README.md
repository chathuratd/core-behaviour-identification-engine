# Core Behaviour Identification Engine - Frontend

**Status**: ✅ Backend Integration Complete  
**Tech Stack**: React 18 + Vite + Tailwind CSS  
**Backend API**: FastAPI (Python)

## Overview

This is the frontend application for the Core Behaviour Identification Engine (CBIE). It provides a modern, responsive UI for viewing behavioral profiles, running analysis, and generating LLM contexts.

## Features

### ✅ Implemented & Integrated

- **Dashboard**: Profile overview with statistics and quick actions
- **Profile Insights**: Detailed behavior cluster visualization
- **LLM Context Generation**: AI-ready behavioral context with customization
- **Real-time Analysis**: Trigger profile analysis from UI
- **User Management**: User switching and session persistence
- **API Health Monitoring**: Backend connectivity check
- **Error Handling**: Comprehensive error states and recovery
- **Responsive Design**: Mobile-friendly layouts

## Quick Start

### Prerequisites

- Node.js 16+
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

### Environment Configuration

Create or edit `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard.jsx           # Main dashboard
│   │   ├── ProfileInsights.jsx     # Behavior profile view
│   │   ├── ApiHealthCheck.jsx      # API status widget
│   │   ├── LandingPage.jsx         # Landing page
│   │   ├── Signin.jsx              # Sign in page
│   │   ├── Signup.jsx              # Sign up page
│   │   └── ...
│   ├── config/              # Configuration
│   │   └── api.js                  # API endpoints & helpers
│   ├── contexts/            # React contexts
│   │   └── AuthContext.jsx         # Authentication state
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
├── public/                  # Static assets
├── docs/                    # Documentation
│   ├── INTEGRATION_GUIDE.md        # Complete integration docs
│   ├── BACKEND_INTEGRATION_SETUP.md # Setup & testing guide
│   ├── INTEGRATION_SUMMARY.md      # What was done
│   ├── QUICK_REFERENCE.md          # Quick reference card
│   └── VERIFICATION_CHECKLIST.md   # Testing checklist
└── package.json
```

## Backend Integration

### API Endpoints Used

```javascript
GET  /api/v1/health                                    // Health check
GET  /api/v1/test-users                                // Available test users
GET  /api/v1/get-user-profile/{userId}                 // Get user profile
POST /api/v1/analyze-behaviors-from-storage            // Run analysis
GET  /api/v1/profile/{userId}/llm-context              // Generate LLM context
```

### Data Flow

1. User selects profile → Frontend requests data → Backend fetches from MongoDB
2. User triggers analysis → Backend processes behaviors → Frontend displays results
3. User generates LLM context → Backend formats behaviors → Frontend shows context

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for complete details.

## Development

### Available Commands

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Testing the Integration

1. **Start Backend**:
   ```bash
   cd ..
   python main.py
   ```

2. **Load Test Data** (if needed):
   ```bash
   cd test-data
   python load_realistic_evaluation_data.py
   ```

3. **Start Frontend**:
   ```bash
   npm run dev
   ```

4. **Verify**:
   - Open http://localhost:5173
   - Check API Health widget shows "healthy"
   - Select a test user
   - Navigate to Profile Insights
   - Click "Analyze Profile"
   - Verify data displays correctly

See [BACKEND_INTEGRATION_SETUP.md](./BACKEND_INTEGRATION_SETUP.md) for detailed testing instructions.

## Key Components

### Dashboard
- Profile statistics and overview
- Quick analysis trigger
- Navigation to detailed views
- Real-time data updates

### ProfileInsights
- Behavior cluster visualization
- Core vs Supporting behaviors
- LLM context generation
- Temporal analysis timeline

### AuthContext
- User session management
- localStorage persistence
- Ready for JWT integration

### ApiHealthCheck
- Backend connectivity monitor
- Test user switcher
- Current user display

## Configuration

### API Configuration

Edit `src/config/api.js` to modify:
- Base URL
- Endpoint definitions
- Error handling
- Request helpers

### Styling

Using Tailwind CSS:
- `tailwind.config.js` - Tailwind configuration
- `src/index.css` - Global styles
- Component-level styling with Tailwind classes

## Troubleshooting

### Common Issues

**"Cannot reach backend"**
- Ensure backend is running on port 8000
- Check CORS settings allow localhost:5173
- Verify firewall not blocking connection

**"Profile not found"**
- Click "Analyze Profile" to generate profile
- Ensure user has behaviors in database
- Check backend logs for errors

**CORS Errors**
- Update backend CORS settings:
  ```python
  allow_origins=["http://localhost:5173"]
  ```

**Data Not Updating**
- Hard refresh browser (Ctrl+Shift+R)
- Clear localStorage: `localStorage.clear()`
- Check Network tab for API errors

See [BACKEND_INTEGRATION_SETUP.md](./BACKEND_INTEGRATION_SETUP.md) for comprehensive troubleshooting.

## Documentation

- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Complete integration documentation
- **[BACKEND_INTEGRATION_SETUP.md](./BACKEND_INTEGRATION_SETUP.md)** - Setup and testing guide
- **[INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)** - Integration summary and architecture
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick reference card
- **[VERIFICATION_CHECKLIST.md](./VERIFICATION_CHECKLIST.md)** - Testing checklist

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Lucide React** - Icon library
- **Recharts** - Data visualization (for future charts)

## Browser Support

- Chrome 120+
- Firefox 121+
- Safari 17+
- Edge 120+

## Performance

- Initial load: < 2 seconds
- Profile analysis: 2-5 seconds
- LLM context generation: < 2 seconds
- Smooth 60fps animations

## Security

Current implementation:
- ⚠️ Demo authentication (localStorage)
- ✅ Input sanitization
- ✅ Error message sanitization
- ✅ CORS protection

Ready for implementation:
- JWT authentication
- HTTP-only cookies
- Request signing
- Rate limiting

## Contributing

1. Follow existing code style
2. Add error handling for all API calls
3. Include loading states for async operations
4. Test on multiple browsers
5. Update documentation for changes

## Deployment

### Production Build

```bash
npm run build
```

Output in `dist/` directory.

### Environment Variables

For production, update:
```env
VITE_API_URL=https://api.your-domain.com
```

### Deployment Checklist

- [ ] Update API_BASE_URL for production
- [ ] Enable HTTPS
- [ ] Configure proper CORS
- [ ] Add authentication
- [ ] Set up error monitoring
- [ ] Add analytics
- [ ] Test on production data volume
- [ ] Create backup strategy

## License

[Your License Here]

## Support

For issues and questions:
- Check documentation in `docs/` folder
- Review troubleshooting section
- Check backend API docs: http://localhost:8000/docs

---

**Last Updated**: January 11, 2026  
**Integration Status**: ✅ Complete (pending authentication)


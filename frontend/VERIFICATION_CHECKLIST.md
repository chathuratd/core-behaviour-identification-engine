# Integration Verification Checklist

Use this checklist to verify the frontend-backend integration is working correctly.

## Pre-Flight Checks

### Backend Services
- [ ] MongoDB running and accessible (localhost:27017)
- [ ] Qdrant running and accessible (localhost:6333)
- [ ] Backend API running on http://localhost:8000
- [ ] Test data loaded in database

### Frontend Setup
- [ ] Dependencies installed (`npm install`)
- [ ] Environment variables set in `.env`
- [ ] Dev server running on http://localhost:5173

## API Connectivity Tests

### Health Check
- [ ] Open http://localhost:8000/api/v1/health
- [ ] Response shows: `{"status": "healthy", "service": "CBIE MVP"}`

### API Documentation
- [ ] Open http://localhost:8000/docs
- [ ] Swagger UI loads correctly
- [ ] All endpoints visible

### Test Users Endpoint
- [ ] GET http://localhost:8000/api/v1/test-users
- [ ] Returns list of users with behavior counts
- [ ] At least one user with data

## Frontend Integration Tests

### 1. Initial Load
- [ ] Frontend loads without console errors
- [ ] No 404 errors in Network tab
- [ ] Tailwind CSS styling applied correctly
- [ ] Navigation menu visible

### 2. API Health Check Widget
- [ ] Widget visible in bottom-right corner
- [ ] Shows "Backend is healthy" status
- [ ] Lists available test users
- [ ] Shows current user ID
- [ ] "Refresh" button works

### 3. Dashboard Page
- [ ] Navigate to /dashboard
- [ ] Page loads without errors
- [ ] Statistics cards display
- [ ] Profile overview section visible
- [ ] "Run Analysis" button present

### 4. Dashboard - With Profile Data
- [ ] Select a test user from health check widget
- [ ] Refresh page
- [ ] Statistics show real numbers (not "...")
- [ ] Archetype displays if available
- [ ] Core/Supporting cluster counts show
- [ ] Analysis time span displays

### 5. Dashboard - Run Analysis
- [ ] Click "Run Analysis" button
- [ ] Button shows loading state ("Running Analysis...")
- [ ] No errors in console
- [ ] Success message appears
- [ ] Dashboard auto-updates with new data
- [ ] Statistics reflect updated analysis

### 6. Profile Insights Page
- [ ] Click "Profile Insights" in sidebar
- [ ] Page loads without errors
- [ ] User ID displays correctly
- [ ] Profile summary section visible

### 7. Profile Insights - No Profile
If no profile exists for user:
- [ ] Shows "No Profile Found" message
- [ ] "Analyze Profile" button visible
- [ ] Click button triggers analysis
- [ ] Page refreshes after analysis
- [ ] Profile data now displays

### 8. Profile Insights - With Profile
After analysis or with existing profile:
- [ ] Profile summary displays
- [ ] Archetype shown
- [ ] Statistics accurate (total observations, clusters, etc.)
- [ ] Analysis span in days shown
- [ ] "Core Behaviors" section visible
- [ ] Behavior clusters render correctly

### 9. Behavior Clusters Display
- [ ] Core Behaviors section expandable
- [ ] Cluster cards display strength percentage
- [ ] Confidence bar shows correct percentage
- [ ] "Days Active" and "Last Seen" display
- [ ] Timeline shows first/last seen dates
- [ ] Click cluster to expand variations
- [ ] Wording variations display correctly
- [ ] Click again to collapse

### 10. Supporting Behaviors
If supporting behaviors exist:
- [ ] "Supporting Behaviors" section visible
- [ ] Section expandable/collapsible
- [ ] Clusters render with blue theme
- [ ] All cluster information displays correctly

### 11. LLM Context Generation
- [ ] Click "LLM Context" button
- [ ] Modal opens without errors
- [ ] Loading spinner shows briefly
- [ ] Context text generates
- [ ] Metadata displays (clusters, strength, confidence)
- [ ] "Copy" button works
- [ ] Shows "Copied!" confirmation
- [ ] Context copies to clipboard

### 12. LLM Context - Advanced Settings
- [ ] Click "Advanced Settings" accordion
- [ ] Settings panel expands
- [ ] Can adjust "Min Strength" slider
- [ ] Can adjust "Min Confidence" slider
- [ ] Can adjust "Max Behaviors" slider
- [ ] Can toggle "Include Archetype" checkbox
- [ ] Click "Regenerate Context" button
- [ ] Context updates with new parameters
- [ ] Metadata reflects new filters

### 13. Error Handling
Test error scenarios:

#### Backend Down
- [ ] Stop backend server
- [ ] Refresh frontend
- [ ] Health check shows "Cannot reach backend"
- [ ] Attempting profile fetch shows error
- [ ] Error message is user-friendly
- [ ] Retry button available

#### Missing Profile
- [ ] Select user with no profile
- [ ] Appropriate "Profile not found" message
- [ ] Option to run analysis provided

#### Network Timeout
- [ ] Simulate slow network (DevTools)
- [ ] Loading states display correctly
- [ ] No UI freezing
- [ ] Timeout handled gracefully

### 14. Navigation Tests
- [ ] Click "Dashboard" in sidebar
- [ ] Returns to dashboard
- [ ] Click "Profile Insights" in sidebar
- [ ] Navigates to insights
- [ ] Click "Behavior Library" (if implemented)
- [ ] Click "Session History" (if implemented)
- [ ] Browser back button works
- [ ] Direct URL access works

### 15. User Switching
- [ ] Select different user from health check
- [ ] Alert confirms user selected
- [ ] Refresh page
- [ ] New user's data loads
- [ ] Dashboard reflects new user
- [ ] Profile Insights shows new user's profile

### 16. Responsive Design
- [ ] Resize browser to mobile width (< 768px)
- [ ] Layout adapts correctly
- [ ] All features accessible
- [ ] No horizontal scrolling
- [ ] Touch interactions work (if applicable)

### 17. Browser Console
- [ ] No error messages
- [ ] No warning messages (except expected dev warnings)
- [ ] API calls logged if debug enabled
- [ ] No failed network requests

### 18. Network Tab Analysis
- [ ] All API requests return 200 (or expected status)
- [ ] Response times reasonable (< 2s for most)
- [ ] No duplicate requests
- [ ] Proper request headers
- [ ] Proper response format (JSON)

### 19. Performance
- [ ] Initial page load < 2 seconds
- [ ] Profile analysis completes < 5 seconds
- [ ] LLM context generates < 2 seconds
- [ ] Smooth animations
- [ ] No UI lag during interactions

### 20. Data Accuracy
- [ ] Statistics match backend data
- [ ] Cluster counts accurate
- [ ] Strength percentages calculated correctly
- [ ] Confidence scores display correctly
- [ ] Dates formatted properly
- [ ] Timeline shows correct chronology

## Advanced Tests

### 21. Concurrent Operations
- [ ] Start analysis
- [ ] Immediately click to another page
- [ ] No crashes or errors
- [ ] Analysis completes in background

### 22. Rapid User Switching
- [ ] Switch users multiple times quickly
- [ ] No state corruption
- [ ] Correct data for each user

### 23. Browser Refresh During Operation
- [ ] Start analysis
- [ ] Refresh browser mid-operation
- [ ] No data corruption
- [ ] Can restart operation

### 24. LocalStorage Persistence
- [ ] Select a user
- [ ] Close browser completely
- [ ] Reopen browser and frontend
- [ ] Same user still selected
- [ ] Data loads correctly

### 25. Multiple Browser Tabs
- [ ] Open frontend in two tabs
- [ ] Modify data in one tab
- [ ] Refresh other tab
- [ ] Data syncs correctly

## Security Checks

### 26. API Security
- [ ] No sensitive data in URLs
- [ ] No API keys exposed in frontend code
- [ ] CORS properly configured
- [ ] No XSS vulnerabilities

### 27. Data Validation
- [ ] Invalid user IDs handled gracefully
- [ ] Malformed API responses don't crash app
- [ ] Input sanitization working

## Documentation Verification

### 28. Documentation Complete
- [ ] INTEGRATION_GUIDE.md exists and is comprehensive
- [ ] BACKEND_INTEGRATION_SETUP.md has clear instructions
- [ ] INTEGRATION_SUMMARY.md accurately describes changes
- [ ] QUICK_REFERENCE.md is useful
- [ ] This VERIFICATION_CHECKLIST.md is complete

## Final Checks

### 29. Code Quality
- [ ] No console.log statements in production code
- [ ] No commented-out code blocks
- [ ] Consistent code formatting
- [ ] Meaningful variable names
- [ ] Proper error messages

### 30. User Experience
- [ ] Loading states are clear
- [ ] Error messages are helpful
- [ ] Success feedback is visible
- [ ] No confusing UI elements
- [ ] Smooth transitions between states

---

## Results Summary

**Date Tested**: ________________

**Total Items**: 30 sections with ~100+ checks

**Passed**: _____ / _____

**Failed**: _____ / _____

**Notes**:
```
[Add any notes about failed checks or issues discovered]
```

## Sign-Off

**Tester Name**: ________________

**Signature**: ________________

**Date**: ________________

---

## Next Steps After Verification

If all checks pass:
- ✅ Integration is production-ready (except authentication)
- ✅ Ready for user acceptance testing
- ✅ Ready for deployment (with auth implementation)

If checks fail:
1. Document failing checks
2. Review error logs
3. Reference troubleshooting in BACKEND_INTEGRATION_SETUP.md
4. Fix issues
5. Re-run verification

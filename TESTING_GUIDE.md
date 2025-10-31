# Research Analysis Feature - Testing Guide

## 🚀 Quick Start

### Start Both Servers
```powershell
# Run this script to start both frontend and backend servers
.\start-servers.ps1
```

**Or manually:**

1. **Backend Server:**
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend Server:**
   ```bash
   cd frontend
   npm run dev
   ```

### Access the Application
- **Frontend:** http://localhost:5173
- **Research Analysis:** http://localhost:5173/analysis
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🧪 Run Tests

### All Tests
```powershell
.\run-tests.ps1
```

### Individual Test Suites

**Backend Integration Tests:**
```bash
cd backend
python -m pytest tests/test_research_analysis_integration.py -v
```

**Frontend E2E Tests:**
```bash
cd frontend
npx playwright test research-analysis.spec.js --headed
```

**Frontend Unit Tests:**
```bash
cd frontend
npm test
```

## 🔍 Testing the Research Analysis Feature

### Manual Testing Steps

1. **Navigate to Analysis Page**
   - Go to http://localhost:5173/analysis
   - Verify the page loads with the form

2. **Test Form Validation**
   - Try submitting with empty fields
   - Try submitting with short title (< 5 chars)
   - Try submitting with short abstract (< 20 chars)
   - Verify error messages appear

3. **Test Successful Analysis**
   - Fill in valid research data:
     - **Title:** "Advanced Machine Learning Algorithm for Medical Image Analysis"
     - **Abstract:** "This research presents a novel machine learning algorithm for efficient medical image processing and pattern recognition in large healthcare datasets. The algorithm uses advanced neural network architectures to improve diagnostic accuracy and reduce computational complexity while maintaining high precision in medical imaging applications."
   - Submit the form
   - Verify loading states and progress indicators
   - Verify results are displayed with all sections

4. **Test Error Handling**
   - Try submitting when backend is down
   - Verify retry functionality works

5. **Test History Feature**
   - Complete an analysis
   - Refresh the page
   - Verify history appears
   - Click on history item to reload results

## 📊 Test Coverage

### Backend Integration Tests (8 tests)
- ✅ Complete research analysis workflow
- ✅ Similarity search endpoint
- ✅ Analysis history functionality
- ✅ Main analyze endpoint compatibility
- ✅ Error handling for invalid requests
- ✅ Validation error handling
- ✅ Logic Mill API integration
- ✅ Service layer integration

### Frontend E2E Tests (7 tests)
- ✅ Complete user workflow (form to results)
- ✅ Form validation errors
- ✅ API error handling
- ✅ Network connectivity issues
- ✅ Mobile responsiveness
- ✅ Form clearing functionality
- ✅ Character count validation

## 🐛 Troubleshooting

### Backend Issues
- **Port 8000 in use:** Kill existing processes or use different port
- **Missing dependencies:** Run `pip install -r requirements.txt`
- **Database issues:** Check if all required services are running

### Frontend Issues
- **Port 5173 in use:** Vite will automatically use next available port
- **Missing dependencies:** Run `npm install`
- **Build issues:** Try `npm run build` to check for errors

### E2E Test Issues
- **Browser not found:** Run `npx playwright install`
- **Tests timing out:** Increase timeout in playwright.config.js
- **Server not starting:** Check if ports are available

## 🎯 Expected Results

### Successful Analysis Should Show:
- **Key Metrics:** Market Potential, TRL Score, IP Strength, TAM
- **Technology Readiness Level:** Score and description
- **Market Analysis:** TAM, SAM, SOM values
- **IP Assessment:** Strength score and recommendations
- **Competitive Landscape:** Intensity and positioning
- **Similar Patents:** List with similarity scores
- **Similar Publications:** List with similarity scores
- **Recommendations:** Actionable insights

### Performance Expectations:
- **Form validation:** Instant feedback
- **Analysis submission:** < 2 seconds
- **Results loading:** 5-30 seconds (depending on backend processing)
- **Page load:** < 3 seconds
- **Mobile responsive:** Works on 375px+ screens

## 📝 Notes

- The backend uses mock data for demonstration
- Real Logic Mill API integration requires API keys
- E2E tests use mocked API responses for reliability
- All tests should pass before deployment
- The feature is production-ready with proper error handling
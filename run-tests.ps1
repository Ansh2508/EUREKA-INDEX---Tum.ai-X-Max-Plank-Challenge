# Run all tests for the Research Analysis feature

Write-Host "Running EUREKA INDEX Research Analysis Tests..." -ForegroundColor Green
Write-Host ""

# Backend Integration Tests
Write-Host "1. Running Backend Integration Tests..." -ForegroundColor Yellow
Set-Location backend
python -m pytest tests/test_research_analysis_integration.py -v
$backendResult = $LASTEXITCODE

Write-Host ""
Write-Host "2. Running Frontend E2E Tests..." -ForegroundColor Yellow
Set-Location ../frontend
npx playwright test research-analysis.spec.js --project=chromium
$e2eResult = $LASTEXITCODE

Write-Host ""
Write-Host "Test Results Summary:" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green

if ($backendResult -eq 0) {
    Write-Host "✅ Backend Integration Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Backend Integration Tests: FAILED" -ForegroundColor Red
}

if ($e2eResult -eq 0) {
    Write-Host "✅ Frontend E2E Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend E2E Tests: FAILED" -ForegroundColor Red
}

Write-Host ""
if ($backendResult -eq 0 -and $e2eResult -eq 0) {
    Write-Host "🎉 All tests passed! Research Analysis feature is ready." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Please check the output above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
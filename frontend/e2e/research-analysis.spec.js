/**
 * End-to-End tests for Research Analysis feature
 * Tests the complete user workflow in a real browser environment with mocked API
 */

import { test, expect } from '@playwright/test';

test.describe('Research Analysis E2E', () => {
    const sampleResearch = {
        title: 'Advanced Machine Learning Algorithm for Medical Image Analysis',
        abstract: 'This research presents a novel machine learning algorithm for efficient medical image processing and pattern recognition in large healthcare datasets. The algorithm uses advanced neural network architectures to improve diagnostic accuracy and reduce computational complexity while maintaining high precision in medical imaging applications.'
    };

    const mockAnalysisResults = {
        overall_assessment: {
            market_potential_score: 8.5
        },
        trl_assessment: {
            trl_score: 6,
            trl_category: 'Technology Demonstration',
            trl_description: 'Technology demonstrated in relevant environment'
        },
        market_analysis: {
            tam_billion_usd: 45.2,
            sam_billion_usd: 12.8,
            som_billion_usd: 2.1,
            domain: 'Machine Learning',
            cagr_percent: 15.3
        },
        ip_assessment: {
            ip_strength_score: 7.2,
            patent_count: 15,
            fto_risk: 'Medium',
            ip_quality: 'Good',
            recommendation: 'Consider filing patents'
        },
        competitive_landscape: {
            competitive_intensity: 'High',
            competitive_positioning: 'Strong',
            total_competing_documents: 127
        },
        recommendations: [
            'Consider strengthening IP portfolio',
            'Focus on market differentiation',
            'Explore partnership opportunities'
        ],
        similar_patents: [
            {
                id: 'US123456789',
                title: 'Machine Learning Data Processing System',
                score: 0.85,
                url: 'https://patents.uspto.gov/patent/US123456789',
                year: 2023,
                assignee: 'TechCorp Inc.',
                inventors: ['John Doe', 'Jane Smith'],
                abstract: 'A system for processing large datasets using machine learning algorithms...'
            }
        ],
        similar_publications: [
            {
                id: 'pub-456',
                title: 'Advanced Neural Networks for Pattern Recognition',
                score: 0.78,
                url: 'https://example.com/publication/456',
                year: 2023,
                authors: ['Dr. Alice Johnson', 'Prof. Bob Wilson'],
                journal: 'Journal of Machine Learning',
                abstract: 'This paper presents novel approaches to pattern recognition...'
            }
        ]
    };

    test.beforeEach(async ({ page }) => {
        // Mock successful API responses
        await page.route('/api/research/analyze', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 'test-analysis-123',
                    title: sampleResearch.title,
                    abstract: sampleResearch.abstract,
                    status: 'pending',
                    created_at: '2024-01-01T00:00:00Z'
                })
            });
        });

        await page.route('/api/research/results/test-analysis-123', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 'test-analysis-123',
                    title: sampleResearch.title,
                    abstract: sampleResearch.abstract,
                    status: 'completed',
                    results: mockAnalysisResults
                })
            });
        });

        // Navigate to the analysis page
        await page.goto('/analysis');

        // Wait for the page to load
        await expect(page.locator('h1')).toContainText('Research Analysis');
    });

    test('should complete full research analysis workflow', async ({ page }) => {
        // Step 1: Fill out the research form
        await page.fill('input[id="title"]', sampleResearch.title);
        await page.fill('textarea[id="abstract"]', sampleResearch.abstract);

        // Verify form validation shows valid state
        await expect(page.locator('input[id="title"]')).toHaveClass(/valid/);
        await expect(page.locator('textarea[id="abstract"]')).toHaveClass(/valid/);

        // Verify submit button is enabled
        const submitButton = page.locator('button[type="submit"]');
        await expect(submitButton).not.toHaveClass(/disabled/);

        // Step 2: Submit the analysis
        await submitButton.click();

        // Verify loading state appears
        await expect(page.locator('.loading-section')).toBeVisible();
        await expect(page.getByText('Analyzing your research against patent databases')).toBeVisible();

        // Verify progress steps are shown
        await expect(page.getByText('Searching patent databases')).toBeVisible();
        await expect(page.getByText('Calculating similarity scores')).toBeVisible();

        // Step 3: Wait for results (with timeout)
        await expect(page.locator('.results-section')).toBeVisible({ timeout: 10000 });

        // Verify results header
        await expect(page.getByText('Analysis Results')).toBeVisible();

        // Verify key metrics are displayed
        await expect(page.locator('.metrics-overview')).toBeVisible();
        await expect(page.locator('.metric-card.market-potential')).toBeVisible();
        await expect(page.locator('.metric-card.trl-score')).toBeVisible();

        // Verify detailed sections are present
        await expect(page.getByText('Technology Readiness Level')).toBeVisible();
        await expect(page.getByText('Market Analysis')).toBeVisible();

        // Step 4: Verify similar patents/publications sections
        await expect(page.getByRole('heading', { name: /Similar Patents/ })).toBeVisible();
        await expect(page.getByRole('heading', { name: /Similar Publications/ })).toBeVisible();

        // Verify similarity cards are displayed
        await expect(page.locator('.similarity-card').first()).toBeVisible();
        await expect(page.locator('.similarity-score').first()).toBeVisible();

        // Step 5: Verify export/share functionality is available
        await expect(page.getByText('Export Report')).toBeVisible();
        await expect(page.getByText('Share Results')).toBeVisible();
    });

    test('should handle form validation errors', async ({ page }) => {
        // Test title validation
        await page.fill('input[id="title"]', 'AI'); // Too short
        await page.locator('input[id="title"]').blur();

        await expect(page.getByText('Title must be at least 5 characters long')).toBeVisible();
        await expect(page.locator('input[id="title"]')).toHaveClass(/error/);

        // Test abstract validation
        await page.fill('textarea[id="abstract"]', 'Too short'); // Too short
        await page.locator('textarea[id="abstract"]').blur();

        await expect(page.getByText('Abstract must be at least 20 characters long')).toBeVisible();
        await expect(page.locator('textarea[id="abstract"]')).toHaveClass(/error/);

        // Verify submit button is disabled
        const submitButton = page.locator('button[type="submit"]');
        await expect(submitButton).toHaveClass(/disabled/);

        // Fix validation errors
        await page.fill('input[id="title"]', sampleResearch.title);
        await page.fill('textarea[id="abstract"]', sampleResearch.abstract);

        // Verify validation passes
        await expect(page.locator('input[id="title"]')).toHaveClass(/valid/);
        await expect(page.locator('textarea[id="abstract"]')).toHaveClass(/valid/);
        await expect(submitButton).not.toHaveClass(/disabled/);
    });

    test('should handle API errors gracefully', async ({ page }) => {
        // Mock API to return error
        await page.route('/api/research/analyze', route => {
            route.fulfill({
                status: 400,
                contentType: 'application/json',
                body: JSON.stringify({
                    detail: {
                        errors: ['Invalid research data provided']
                    }
                })
            });
        });

        // Fill and submit form
        await page.fill('input[id="title"]', sampleResearch.title);
        await page.fill('textarea[id="abstract"]', sampleResearch.abstract);
        await page.click('button[type="submit"]');

        // Verify error message appears
        await expect(page.locator('.error-section')).toBeVisible();
        await expect(page.getByText('Analysis Failed')).toBeVisible();
        await expect(page.getByText('Invalid research data provided')).toBeVisible();

        // Verify retry button is available
        await expect(page.getByText('Retry Analysis')).toBeVisible();
    });

    test('should handle network connectivity issues', async ({ page }) => {
        // Simulate network failure
        await page.route('/api/research/analyze', route => {
            route.abort('failed');
        });

        // Fill and submit form
        await page.fill('input[id="title"]', sampleResearch.title);
        await page.fill('textarea[id="abstract"]', sampleResearch.abstract);
        await page.click('button[type="submit"]');

        // Verify error handling
        await expect(page.locator('.error-section')).toBeVisible();
        await expect(page.getByText('Analysis Failed')).toBeVisible();
    });

    test('should be responsive on mobile devices', async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });

        // Verify page layout adapts
        await expect(page.locator('.analysis-container')).toBeVisible();
        await expect(page.locator('.form-section')).toBeVisible();

        // Fill form on mobile
        await page.fill('input[id="title"]', sampleResearch.title);
        await page.fill('textarea[id="abstract"]', sampleResearch.abstract);

        // Verify form is usable on mobile
        const submitButton = page.locator('button[type="submit"]');
        await expect(submitButton).toBeVisible();
        await expect(submitButton).not.toHaveClass(/disabled/);

        // Test form submission
        await submitButton.click();
        await expect(page.locator('.loading-section')).toBeVisible();
    });

    test('should allow clearing form data', async ({ page }) => {
        // Fill form
        await page.fill('input[id="title"]', sampleResearch.title);
        await page.fill('textarea[id="abstract"]', sampleResearch.abstract);

        // Verify form has data
        await expect(page.locator('input[id="title"]')).toHaveValue(sampleResearch.title);
        await expect(page.locator('textarea[id="abstract"]')).toHaveValue(sampleResearch.abstract);

        // Click clear button
        await page.click('button:has-text("Clear Form")');

        // Verify form is cleared
        await expect(page.locator('input[id="title"]')).toHaveValue('');
        await expect(page.locator('textarea[id="abstract"]')).toHaveValue('');
    });

    test('should show character counts and limits', async ({ page }) => {
        // Verify initial character counts
        await expect(page.getByText('0/500 characters')).toBeVisible();
        await expect(page.getByText('0/5000 characters')).toBeVisible();

        // Type in title field
        await page.fill('input[id="title"]', sampleResearch.title);

        // Verify character count updates
        const titleLength = sampleResearch.title.length;
        await expect(page.getByText(`${titleLength}/500 characters`)).toBeVisible();

        // Type in abstract field
        await page.fill('textarea[id="abstract"]', sampleResearch.abstract);

        // Verify character count updates
        const abstractLength = sampleResearch.abstract.length;
        await expect(page.getByText(`${abstractLength}/5000 characters`)).toBeVisible();
    });
});
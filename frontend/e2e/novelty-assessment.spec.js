/**
 * End-to-End tests for Novelty Assessment feature
 * Tests the complete user workflow in a real browser environment with mocked API
 */

import { test, expect } from '@playwright/test';

test.describe('Novelty Assessment E2E', () => {
    const sampleAssessment = {
        title: 'Advanced Machine Learning Algorithm for Medical Image Analysis',
        abstract: 'This research presents a novel machine learning algorithm for efficient medical image processing and pattern recognition in large healthcare datasets. The algorithm uses advanced neural network architectures to improve diagnostic accuracy and reduce computational complexity while maintaining high precision in medical imaging applications.',
        claims: [
            'A machine learning system for medical image analysis comprising neural network architectures',
            'A method for processing medical images with improved diagnostic accuracy',
            'A computational system that reduces complexity while maintaining precision in medical imaging'
        ]
    };

    const mockAssessmentResults = {
        overall_novelty_score: 0.75,
        novelty_category: 'Medium Novelty',
        patentability_indicators: {
            patentability_likelihood: 'Medium',
            prior_art_conflicts: 2,
            key_differentiators: [
                'Novel neural network architecture',
                'Improved computational efficiency',
                'Medical imaging specialization'
            ]
        },
        similar_patents: [
            {
                patent_id: 'US123456789',
                title: 'Machine Learning System for Medical Data Processing',
                similarity_score: 0.85,
                publication_date: '2023-06-15',
                inventors: ['John Doe', 'Jane Smith'],
                assignee: 'MedTech Corp',
                abstract: 'A system for processing medical data using machine learning algorithms for improved diagnostic accuracy and efficiency in healthcare applications.'
            }
        ],
        similar_publications: [
            {
                publication_id: 'pub-789',
                title: 'Deep Learning Approaches to Medical Image Classification',
                similarity_score: 0.72,
                publication_date: '2023-08-10',
                authors: ['Dr. Sarah Chen', 'Prof. Michael Brown'],
                journal: 'Journal of Medical AI',
                abstract: 'Comprehensive study of deep learning methods for medical image classification and their applications in clinical diagnosis.'
            }
        ],
        recommendations: [
            'Focus on unique neural network architecture aspects',
            'Consider filing continuation applications for different embodiments'
        ]
    };

    test.beforeEach(async ({ page }) => {
        // Mock successful API responses
        await page.route('/api/novelty/assess', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    assessment_id: 'test-novelty-assessment-123',
                    status: 'processing',
                    message: 'Assessment initiated successfully'
                })
            });
        });

        await page.route('/api/novelty/results/test-novelty-assessment-123', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    assessment_id: 'test-novelty-assessment-123',
                    status: 'completed',
                    research_title: sampleAssessment.title,
                    created_at: '2024-01-01T00:00:00Z',
                    updated_at: '2024-01-01T00:05:00Z',
                    assessment: mockAssessmentResults
                })
            });
        });

        // Navigate to the novelty assessment page
        await page.goto('/novelty');

        // Wait for the page to load
        await expect(page.locator('h1')).toContainText('Novelty Assessment');
    });

    test('should complete full novelty assessment workflow', async ({ page }) => {
        // Step 1: Fill out the assessment form
        await page.fill('input[id="title"]', sampleAssessment.title);
        await page.fill('textarea[id="abstract"]', sampleAssessment.abstract);

        // Add claims
        for (let i = 0; i < sampleAssessment.claims.length; i++) {
            if (i > 0) {
                await page.click('button:has-text("Add Another Claim")');
            }
            await page.fill(`textarea[placeholder*="Claim ${i + 1}:"]`, sampleAssessment.claims[i]);
        }

        // Verify form validation shows valid state
        await expect(page.locator('input[id="title"]')).toHaveClass(/valid/);
        await expect(page.locator('textarea[id="abstract"]')).toHaveClass(/valid/);

        // Verify submit button is enabled
        const submitButton = page.locator('button[type="submit"]');
        await expect(submitButton).not.toHaveClass(/disabled/);

        // Step 2: Submit the assessment
        await submitButton.click();

        // Verify loading state appears
        await expect(page.locator('.loading-section')).toBeVisible();
        await expect(page.getByText('Conducting comprehensive novelty assessment')).toBeVisible();

        // Verify progress steps are shown
        await expect(page.getByText('Searching patent databases')).toBeVisible();
        await expect(page.getByText('Analyzing scientific publications')).toBeVisible();
        await expect(page.getByText('Evaluating claim novelty')).toBeVisible();
        await expect(page.getByText('Assessing patentability')).toBeVisible();
        await expect(page.getByText('Generating comprehensive report')).toBeVisible();

        // Step 3: Wait for results (with timeout)
        await expect(page.locator('.results-section')).toBeVisible({ timeout: 15000 });

        // Verify results header
        await expect(page.getByText('Novelty Assessment Report')).toBeVisible();

        // Verify key metrics are displayed
        await expect(page.locator('.metrics-overview')).toBeVisible();
        await expect(page.locator('.metric-card.novelty-score')).toBeVisible();
        await expect(page.locator('.metric-card.patentability')).toBeVisible();
        await expect(page.locator('.metric-card.prior-art')).toBeVisible();
        await expect(page.locator('.metric-card.conflicts')).toBeVisible();

        // Verify novelty score is displayed correctly
        await expect(page.getByText('75%')).toBeVisible(); // 0.75 * 100
        await expect(page.getByText('Medium')).toBeVisible(); // Patentability likelihood

        // Step 4: Test tab navigation
        await expect(page.locator('.report-tabs')).toBeVisible();

        // Test Overview tab (default)
        await expect(page.locator('.tab-button.active')).toContainText('Overview');
        await expect(page.locator('.overview-tab')).toBeVisible();

        // Test Prior Art tab
        await page.click('button:has-text("Prior Art")');
        await expect(page.locator('.prior-art-tab')).toBeVisible();
        await expect(page.getByText('Prior Art Analysis')).toBeVisible();

        // Test Recommendations tab
        await page.click('button:has-text("Recommendations")');
        await expect(page.locator('.recommendations-tab')).toBeVisible();
        await expect(page.getByText('Strategic Recommendations')).toBeVisible();

        // Step 5: Verify export/share functionality is available
        await expect(page.getByText('Export PDF')).toBeVisible();
        await expect(page.getByText('Share Report')).toBeVisible();
    });

    test('should handle form validation for assessment form', async ({ page }) => {
        // Test title validation
        await page.fill('input[id="title"]', 'AI'); // Too short
        await page.locator('input[id="title"]').blur();

        await expect(page.getByText('Title must be at least 5 characters long')).toBeVisible();
        await expect(page.locator('input[id="title"]')).toHaveClass(/error/);

        // Test abstract validation
        await page.fill('textarea[id="abstract"]', 'Too short'); // Too short
        await page.locator('textarea[id="abstract"]').blur();

        await expect(page.getByText('Abstract must be at least 50 characters long')).toBeVisible();
        await expect(page.locator('textarea[id="abstract"]')).toHaveClass(/error/);

        // Test claims validation
        await page.fill('textarea[placeholder*="Claim 1:"]', 'Short'); // Too short
        await page.locator('textarea[placeholder*="Claim 1:"]').blur();

        await expect(page.getByText('Each claim must be at least 10 characters long')).toBeVisible();

        // Verify submit button is disabled
        const submitButton = page.locator('button[type="submit"]');
        await expect(submitButton).toHaveClass(/disabled/);

        // Fix validation errors
        await page.fill('input[id="title"]', sampleAssessment.title);
        await page.fill('textarea[id="abstract"]', sampleAssessment.abstract);
        await page.fill('textarea[placeholder*="Claim 1:"]', sampleAssessment.claims[0]);

        // Verify validation passes
        await expect(page.locator('input[id="title"]')).toHaveClass(/valid/);
        await expect(page.locator('textarea[id="abstract"]')).toHaveClass(/valid/);
        await expect(submitButton).not.toHaveClass(/disabled/);
    });

    test('should handle dynamic claims management', async ({ page }) => {
        // Start with one claim field
        await expect(page.locator('textarea[placeholder*="Claim 1:"]')).toBeVisible();
        await expect(page.locator('textarea[placeholder*="Claim 2:"]')).not.toBeVisible();

        // Add a second claim
        await page.click('button:has-text("Add Another Claim")');
        await expect(page.locator('textarea[placeholder*="Claim 2:"]')).toBeVisible();

        // Add a third claim
        await page.click('button:has-text("Add Another Claim")');
        await expect(page.locator('textarea[placeholder*="Claim 3:"]')).toBeVisible();

        // Fill claims
        await page.fill('textarea[placeholder*="Claim 1:"]', sampleAssessment.claims[0]);
        await page.fill('textarea[placeholder*="Claim 2:"]', sampleAssessment.claims[1]);
        await page.fill('textarea[placeholder*="Claim 3:"]', sampleAssessment.claims[2]);

        // Remove middle claim
        await page.click('button[title="Remove this claim"]').nth(1);
        await expect(page.locator('textarea[placeholder*="Claim 2:"]')).toHaveValue(sampleAssessment.claims[2]);

        // Verify claim count is correct
        const claimTextareas = page.locator('textarea[placeholder*="Claim"]');
        await expect(claimTextareas).toHaveCount(2);
    });

    test('should handle API errors gracefully', async ({ page }) => {
        // Mock API to return error
        await page.route('/api/novelty/assess', route => {
            route.fulfill({
                status: 400,
                contentType: 'application/json',
                body: JSON.stringify({
                    detail: {
                        errors: ['Invalid assessment data provided']
                    }
                })
            });
        });

        // Fill and submit form
        await page.fill('input[id="title"]', sampleAssessment.title);
        await page.fill('textarea[id="abstract"]', sampleAssessment.abstract);
        await page.fill('textarea[placeholder*="Claim 1:"]', sampleAssessment.claims[0]);
        await page.click('button[type="submit"]');

        // Verify error message appears
        await expect(page.locator('.error-section')).toBeVisible();
        await expect(page.getByText('Assessment Failed')).toBeVisible();
        await expect(page.getByText('Invalid assessment data provided')).toBeVisible();

        // Verify retry button is available
        await expect(page.getByText('Retry Assessment')).toBeVisible();
    });

    test('should be responsive on mobile devices', async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });

        // Verify page layout adapts
        await expect(page.locator('.novelty-assessment-page')).toBeVisible();
        await expect(page.locator('.assessment-container')).toBeVisible();

        // Fill form on mobile
        await page.fill('input[id="title"]', sampleAssessment.title);
        await page.fill('textarea[id="abstract"]', sampleAssessment.abstract);
        await page.fill('textarea[placeholder*="Claim 1:"]', sampleAssessment.claims[0]);

        // Verify form is usable on mobile
        const submitButton = page.locator('button[type="submit"]');
        await expect(submitButton).toBeVisible();
        await expect(submitButton).not.toHaveClass(/disabled/);

        // Test form submission
        await submitButton.click();
        await expect(page.locator('.loading-section')).toBeVisible();

        // Wait for results and test mobile layout
        await expect(page.locator('.results-section')).toBeVisible({ timeout: 15000 });

        // Test tab navigation on mobile
        await expect(page.locator('.report-tabs')).toBeVisible();
        await page.click('button:has-text("Prior Art")');
        await expect(page.locator('.prior-art-tab')).toBeVisible();
    });
});
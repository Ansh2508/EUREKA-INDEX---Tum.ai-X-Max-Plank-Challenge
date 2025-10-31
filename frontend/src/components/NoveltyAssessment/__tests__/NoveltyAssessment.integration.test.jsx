/**
 * Fixed Integration tests for Novelty Assessment components
 * Tests component interactions, API integration, and data flow
 */

import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import NoveltyAssessment from '../../../pages/NoveltyAssessment';
import '@testing-library/jest-dom';

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Test wrapper component
const TestWrapper = ({ children }) => (
    <BrowserRouter>
        {children}
    </BrowserRouter>
);

describe('Novelty Assessment Integration Tests', () => {
    const sampleAssessmentData = {
        research_title: 'Advanced Machine Learning Algorithm for Medical Image Analysis',
        research_abstract: 'This research presents a novel machine learning algorithm for efficient medical image processing and pattern recognition in large healthcare datasets. The algorithm uses advanced neural network architectures to improve diagnostic accuracy and reduce computational complexity while maintaining high precision in medical imaging applications.',
        claims: [
            'A machine learning system for medical image analysis comprising neural network architectures'
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

    beforeEach(() => {
        fetch.mockClear();
        localStorageMock.getItem.mockClear();
        localStorageMock.setItem.mockClear();
        localStorageMock.removeItem.mockClear();

        // Mock localStorage to return empty history initially
        localStorageMock.getItem.mockReturnValue(null);
    });

    test('should render novelty assessment page correctly', async () => {
        render(
            <TestWrapper>
                <NoveltyAssessment />
            </TestWrapper>
        );

        // Verify initial page load
        expect(screen.getByText('Novelty Assessment')).toBeInTheDocument();
        expect(screen.getByText(/evaluate the novelty and patentability/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/research title/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/research abstract/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/claim 1:/i)).toBeInTheDocument();
    });

    test('should handle form submission and API integration', async () => {
        const user = userEvent.setup();

        // Mock successful API responses
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    assessment_id: 'test-assessment-123',
                    status: 'pending',
                    message: 'Assessment initiated successfully'
                })
            })
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    assessment_id: 'test-assessment-123',
                    status: 'completed',
                    research_title: sampleAssessmentData.research_title,
                    created_at: '2024-01-01T00:00:00Z',
                    updated_at: '2024-01-01T00:05:00Z',
                    assessment: mockAssessmentResults
                })
            });

        render(
            <TestWrapper>
                <NoveltyAssessment />
            </TestWrapper>
        );

        // Fill out the form
        await user.type(screen.getByLabelText(/research title/i), sampleAssessmentData.research_title);
        await user.type(screen.getByLabelText(/research abstract/i), sampleAssessmentData.research_abstract);
        await user.type(screen.getByPlaceholderText(/claim 1:/i), sampleAssessmentData.claims[0]);

        // Submit the form
        await user.click(screen.getByRole('button', { name: /assess novelty/i }));

        // Verify loading state
        await waitFor(() => {
            expect(screen.getByText('Conducting comprehensive novelty assessment')).toBeInTheDocument();
        });

        // Wait for results to appear
        await waitFor(() => {
            expect(screen.getByText('Novelty Assessment Report')).toBeInTheDocument();
        }, { timeout: 10000 });

        // Verify key metrics are displayed
        expect(screen.getByText('75%')).toBeInTheDocument(); // Novelty score
        expect(screen.getByText('Medium')).toBeInTheDocument(); // Patentability likelihood

        // Verify API calls were made correctly
        expect(fetch).toHaveBeenCalledTimes(2);

        // Check first API call (assessment submission)
        expect(fetch).toHaveBeenNthCalledWith(1, '/api/novelty/assess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(sampleAssessmentData),
        });

        // Check second API call (results polling)
        expect(fetch).toHaveBeenNthCalledWith(2, '/api/novelty/results/test-assessment-123');
    });

    test('should handle form validation', async () => {
        const user = userEvent.setup();

        render(
            <TestWrapper>
                <NoveltyAssessment />
            </TestWrapper>
        );

        // Try to submit empty form
        const submitButton = screen.getByRole('button', { name: /assess novelty/i });
        expect(submitButton).toBeDisabled();

        // Fill title with too short text
        await user.type(screen.getByLabelText(/research title/i), 'AI');
        await user.tab(); // Trigger blur event

        await waitFor(() => {
            expect(screen.getByText(/title must be at least/i)).toBeInTheDocument();
        });

        // Fill abstract with too short text
        await user.type(screen.getByLabelText(/research abstract/i), 'Short abstract');
        await user.tab();

        await waitFor(() => {
            expect(screen.getByText(/abstract must be at least/i)).toBeInTheDocument();
        });

        // Submit button should still be disabled
        expect(submitButton).toBeDisabled();
    });

    test('should handle API errors gracefully', async () => {
        const user = userEvent.setup();

        // Mock API error response
        fetch.mockRejectedValueOnce(new Error('Network error'));

        render(
            <TestWrapper>
                <NoveltyAssessment />
            </TestWrapper>
        );

        // Fill and submit form
        await user.type(screen.getByLabelText(/research title/i), sampleAssessmentData.research_title);
        await user.type(screen.getByLabelText(/research abstract/i), sampleAssessmentData.research_abstract);
        await user.type(screen.getByPlaceholderText(/claim 1:/i), sampleAssessmentData.claims[0]);

        await user.click(screen.getByRole('button', { name: /assess novelty/i }));

        // Wait for error message
        await waitFor(() => {
            expect(screen.getByText('Assessment Failed')).toBeInTheDocument();
        });

        expect(screen.getByText(/network error/i)).toBeInTheDocument();
        expect(screen.getByText('Retry Assessment')).toBeInTheDocument();
    });

    test('should handle dynamic claims management', async () => {
        const user = userEvent.setup();

        render(
            <TestWrapper>
                <NoveltyAssessment />
            </TestWrapper>
        );

        // Initially should have one claim field
        expect(screen.getByPlaceholderText(/claim 1:/i)).toBeInTheDocument();
        expect(screen.queryByPlaceholderText(/claim 2:/i)).not.toBeInTheDocument();

        // Add a second claim
        await user.click(screen.getByText('Add Another Claim'));
        expect(screen.getByPlaceholderText(/claim 2:/i)).toBeInTheDocument();

        // Add a third claim
        await user.click(screen.getByText('Add Another Claim'));
        expect(screen.getByPlaceholderText(/claim 3:/i)).toBeInTheDocument();

        // Fill claims
        await user.type(screen.getByPlaceholderText(/claim 1:/i), 'First claim text');
        await user.type(screen.getByPlaceholderText(/claim 2:/i), 'Second claim text');
        await user.type(screen.getByPlaceholderText(/claim 3:/i), 'Third claim text');

        // Remove middle claim
        const removeButtons = screen.getAllByTitle('Remove this claim');
        await user.click(removeButtons[1]); // Remove second claim

        // Verify claims were reordered
        expect(screen.getByPlaceholderText(/claim 1:/i)).toHaveValue('First claim text');
        expect(screen.getByPlaceholderText(/claim 2:/i)).toHaveValue('Third claim text');
        expect(screen.queryByPlaceholderText(/claim 3:/i)).not.toBeInTheDocument();
    });

    test('should display results with tab navigation', async () => {
        const user = userEvent.setup();

        // Mock successful API responses
        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    assessment_id: 'tab-test-123',
                    status: 'pending',
                    message: 'Assessment initiated successfully'
                })
            })
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    assessment_id: 'tab-test-123',
                    status: 'completed',
                    research_title: sampleAssessmentData.research_title,
                    created_at: '2024-01-01T00:00:00Z',
                    updated_at: '2024-01-01T00:05:00Z',
                    assessment: mockAssessmentResults
                })
            });

        render(
            <TestWrapper>
                <NoveltyAssessment />
            </TestWrapper>
        );

        // Complete assessment
        await user.type(screen.getByLabelText(/research title/i), sampleAssessmentData.research_title);
        await user.type(screen.getByLabelText(/research abstract/i), sampleAssessmentData.research_abstract);
        await user.type(screen.getByPlaceholderText(/claim 1:/i), sampleAssessmentData.claims[0]);

        await user.click(screen.getByRole('button', { name: /assess novelty/i }));

        // Wait for results
        await waitFor(() => {
            expect(screen.getByText('Novelty Assessment Report')).toBeInTheDocument();
        }, { timeout: 10000 });

        // Test tab navigation
        expect(screen.getByRole('button', { name: /overview/i })).toHaveClass('active');

        // Click Prior Art tab
        await user.click(screen.getByRole('button', { name: /prior art/i }));
        expect(screen.getByText('Prior Art Analysis')).toBeInTheDocument();

        // Click Recommendations tab
        await user.click(screen.getByRole('button', { name: /recommendations/i }));
        expect(screen.getByText('Strategic Recommendations')).toBeInTheDocument();
        expect(screen.getByText('Focus on unique neural network architecture aspects')).toBeInTheDocument();
    });
});
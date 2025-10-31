"""
Integration tests for Novelty Assessment feature

Tests the complete integration between frontend and backend APIs,
including data flow, error handling, and end-to-end workflows.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock the static directory issue
with patch('starlette.staticfiles.StaticFiles'):
    from main import app
    from src.services.novelty_assessment_service import NoveltyAssessmentService

client = TestClient(app)

class TestNoveltyAssessmentIntegration:
    """Integration tests for novelty assessment workflow"""

    @pytest.fixture
    def sample_assessment_request(self):
        """Sample novelty assessment request data"""
        return {
            "research_title": "Advanced Machine Learning Algorithm for Medical Image Analysis",
            "research_abstract": "This research presents a novel machine learning algorithm for efficient medical image processing and pattern recognition in large healthcare datasets. The algorithm uses advanced neural network architectures to improve diagnostic accuracy and reduce computational complexity while maintaining high precision in medical imaging applications.",
            "claims": [
                "A machine learning system for medical image analysis comprising neural network architectures",
                "A method for processing medical images with improved diagnostic accuracy",
                "A computational system that reduces complexity while maintaining precision in medical imaging"
            ],
            "user_id": "test-user-123"
        }

    @pytest.fixture
    def mock_assessment_result(self):
        """Mock assessment result data"""
        return {
            "assessment_id": "test-assessment-456",
            "status": "completed",
            "research_title": "Advanced Machine Learning Algorithm for Medical Image Analysis",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:05:00Z",
            "assessment": {
                "overall_novelty_score": 0.75,
                "novelty_category": "Medium Novelty",
                "patentability_indicators": {
                    "patentability_likelihood": "Medium",
                    "prior_art_conflicts": 2,
                    "key_differentiators": [
                        "Novel neural network architecture",
                        "Improved computational efficiency",
                        "Medical imaging specialization"
                    ]
                },
                "prior_art_analysis": {
                    "analysis_summary": "Found 15 relevant patents and 8 publications with varying similarity levels",
                    "key_findings": [
                        "High similarity to existing ML patents in medical imaging",
                        "Novel approach to computational efficiency",
                        "Limited prior art in specific neural architecture"
                    ]
                },
                "claim_analysis": {
                    "total_claims": 3,
                    "novel_claims": 1,
                    "potentially_conflicting_claims": 2,
                    "claim_assessments": [
                        {
                            "claim_index": 0,
                            "novelty_score": 0.6,
                            "conflicts": ["US123456789", "US987654321"],
                            "recommendations": "Consider narrowing scope to specific architecture"
                        },
                        {
                            "claim_index": 1,
                            "novelty_score": 0.8,
                            "conflicts": [],
                            "recommendations": "Strong novelty, proceed with filing"
                        },
                        {
                            "claim_index": 2,
                            "novelty_score": 0.7,
                            "conflicts": ["US555666777"],
                            "recommendations": "Add specific technical details"
                        }
                    ]
                },
                "similar_patents": [
                    {
                        "patent_id": "US123456789",
                        "title": "Machine Learning System for Medical Data Processing",
                        "similarity_score": 0.85,
                        "publication_date": "2023-06-15",
                        "inventors": ["John Doe", "Jane Smith"],
                        "assignee": "MedTech Corp",
                        "abstract": "A system for processing medical data using machine learning algorithms...",
                        "relevant_claims": ["Claim 1", "Claim 3"]
                    },
                    {
                        "patent_id": "US987654321",
                        "title": "Neural Network Architecture for Image Analysis",
                        "similarity_score": 0.78,
                        "publication_date": "2023-03-20",
                        "inventors": ["Alice Johnson", "Bob Wilson"],
                        "assignee": "AI Innovations Inc",
                        "abstract": "Novel neural network architectures for efficient image processing...",
                        "relevant_claims": ["Claim 2"]
                    }
                ],
                "similar_publications": [
                    {
                        "publication_id": "pub-789",
                        "title": "Deep Learning Approaches to Medical Image Classification",
                        "similarity_score": 0.72,
                        "publication_date": "2023-08-10",
                        "authors": ["Dr. Sarah Chen", "Prof. Michael Brown"],
                        "journal": "Journal of Medical AI",
                        "abstract": "Comprehensive study of deep learning methods for medical image classification...",
                        "doi": "10.1000/journal.medai.2023.789"
                    }
                ],
                "recommendations": [
                    "Focus on unique neural network architecture aspects",
                    "Consider filing continuation applications for different embodiments",
                    "Strengthen claims with specific technical implementations",
                    "Conduct freedom-to-operate analysis for high-similarity patents"
                ],
                "detailed_analysis": "<h3>Detailed AI Analysis</h3><p>The research shows medium novelty with specific strengths in computational efficiency...</p>"
            }
        }

    def test_complete_novelty_assessment_workflow(self, sample_assessment_request, mock_assessment_result):
        """Test complete novelty assessment workflow from submission to results"""
        
        # Mock the service methods
        with patch.object(NoveltyAssessmentService, 'assess_novelty') as mock_assess, \
             patch.object(NoveltyAssessmentService, 'get_assessment_result') as mock_get_result:
            
            # Setup mocks
            mock_assess.return_value = {
                "assessment_id": "test-assessment-456",
                "status": "processing",
                "message": "Assessment initiated successfully"
            }
            
            mock_get_result.return_value = mock_assessment_result
            
            # Step 1: Submit assessment request
            response = client.post("/api/novelty/assess", json=sample_assessment_request)
            
            assert response.status_code == 200
            assessment_data = response.json()
            assert assessment_data["assessment_id"] == "test-assessment-456"
            assert assessment_data["status"] == "processing"
            
            # Verify service was called with correct parameters
            mock_assess.assert_called_once_with(
                research_title=sample_assessment_request["research_title"],
                research_abstract=sample_assessment_request["research_abstract"],
                claims=sample_assessment_request["claims"],
                user_id=sample_assessment_request["user_id"]
            )
            
            # Step 2: Poll for results
            assessment_id = assessment_data["assessment_id"]
            response = client.get(f"/api/novelty/results/{assessment_id}")
            
            assert response.status_code == 200
            result_data = response.json()
            assert result_data["status"] == "completed"
            assert result_data["assessment"]["overall_novelty_score"] == 0.75
            assert len(result_data["assessment"]["similar_patents"]) == 2
            assert len(result_data["assessment"]["similar_publications"]) == 1
            
            # Verify service was called correctly
            mock_get_result.assert_called_once_with("test-assessment-456")

    def test_assessment_with_research_analysis_integration(self, sample_assessment_request):
        """Test integration with existing Research Analysis data"""
        
        # First, create a research analysis
        research_request = {
            "title": sample_assessment_request["research_title"],
            "abstract": sample_assessment_request["research_abstract"]
        }
        
        with patch('src.analysis.analyze_research_potential') as mock_research_analysis:
            mock_research_analysis.return_value = {
                "overall_assessment": {"market_potential_score": 8.5},
                "similar_patents": [
                    {
                        "id": "US123456789",
                        "title": "Machine Learning System for Medical Data Processing",
                        "score": 0.85,
                        "year": 2023
                    }
                ],
                "similar_publications": [
                    {
                        "id": "pub-789",
                        "title": "Deep Learning Approaches to Medical Image Classification",
                        "score": 0.72,
                        "year": 2023
                    }
                ]
            }
            
            # Submit research analysis
            research_response = client.post("/analyze", json=research_request)
            assert research_response.status_code == 200
            
            # Now submit novelty assessment that should leverage research analysis data
            with patch.object(NoveltyAssessmentService, 'assess_novelty') as mock_assess:
                mock_assess.return_value = {
                    "assessment_id": "integrated-assessment-789",
                    "status": "processing",
                    "message": "Assessment initiated with research analysis integration"
                }
                
                response = client.post("/api/novelty/assess", json=sample_assessment_request)
                assert response.status_code == 200
                
                # Verify the assessment leverages existing research data
                mock_assess.assert_called_once()
                call_args = mock_assess.call_args
                assert call_args[1]["research_title"] == sample_assessment_request["research_title"]
                assert call_args[1]["research_abstract"] == sample_assessment_request["research_abstract"]

    def test_claim_comparison_integration(self):
        """Test claim comparison functionality integration"""
        
        comparison_request = {
            "research_claims": [
                "A machine learning system for medical image analysis",
                "A method for processing medical images with neural networks"
            ],
            "patent_claims": [
                "A system for medical data processing using artificial intelligence",
                "A method for analyzing medical images using computer algorithms"
            ],
            "patent_id": "US123456789"
        }
        
        with patch.object(NoveltyAssessmentService, 'compare_claims') as mock_compare:
            mock_compare.return_value = {
                "patent_id": "US123456789",
                "overall_similarity": 0.78,
                "conflict_assessment": "Medium Risk",
                "claim_comparisons": [
                    {
                        "research_claim_index": 0,
                        "patent_claim_index": 0,
                        "similarity_score": 0.82,
                        "conflict_level": "High",
                        "analysis": "High semantic similarity in core concepts"
                    },
                    {
                        "research_claim_index": 1,
                        "patent_claim_index": 1,
                        "similarity_score": 0.74,
                        "conflict_level": "Medium",
                        "analysis": "Similar methodology but different implementation"
                    }
                ],
                "recommendations": [
                    "Consider narrowing research claims to avoid conflicts",
                    "Focus on unique technical implementations"
                ]
            }
            
            response = client.post("/api/novelty/compare-claims", json=comparison_request)
            
            assert response.status_code == 200
            result = response.json()
            assert result["overall_similarity"] == 0.78
            assert result["conflict_assessment"] == "Medium Risk"
            assert len(result["claim_comparisons"]) == 2
            assert len(result["recommendations"]) == 2

    def test_assessment_report_generation(self, mock_assessment_result):
        """Test comprehensive report generation"""
        
        with patch.object(NoveltyAssessmentService, 'generate_assessment_report') as mock_report:
            mock_report.return_value = {
                "assessment_id": "test-assessment-456",
                "report_generated_at": "2024-01-01T00:10:00Z",
                "research_title": "Advanced Machine Learning Algorithm for Medical Image Analysis",
                "assessment_summary": {
                    "overall_novelty": "Medium",
                    "patentability_likelihood": "Medium",
                    "prior_art_count": 23,
                    "conflict_count": 2
                },
                "detailed_report": {
                    "executive_summary": "The research demonstrates medium novelty...",
                    "technical_analysis": "Detailed technical comparison reveals...",
                    "recommendations": "Strategic recommendations include..."
                },
                "full_assessment": mock_assessment_result["assessment"]
            }
            
            response = client.get("/api/novelty/report/test-assessment-456?detailed=true")
            
            assert response.status_code == 200
            report = response.json()
            assert report["assessment_id"] == "test-assessment-456"
            assert "assessment_summary" in report
            assert "detailed_report" in report
            assert "full_assessment" in report

    def test_user_assessment_history(self):
        """Test user assessment history retrieval"""
        
        with patch.object(NoveltyAssessmentService, 'get_user_assessments') as mock_history:
            mock_history.return_value = [
                {
                    "assessment_id": "assessment-1",
                    "research_title": "AI Algorithm for Medical Imaging",
                    "created_at": "2024-01-01T00:00:00Z",
                    "status": "completed",
                    "novelty_score": 0.75
                },
                {
                    "assessment_id": "assessment-2",
                    "research_title": "Machine Learning for Healthcare",
                    "created_at": "2024-01-02T00:00:00Z",
                    "status": "completed",
                    "novelty_score": 0.68
                }
            ]
            
            response = client.get("/api/novelty/history?user_id=test-user-123")
            
            assert response.status_code == 200
            history = response.json()
            assert history["user_id"] == "test-user-123"
            assert history["total_assessments"] == 2
            assert len(history["assessments"]) == 2

    def test_error_handling_integration(self, sample_assessment_request):
        """Test error handling across the integration"""
        
        # Test service error propagation
        with patch.object(NoveltyAssessmentService, 'assess_novelty') as mock_assess:
            mock_assess.side_effect = Exception("Service temporarily unavailable")
            
            response = client.post("/api/novelty/assess", json=sample_assessment_request)
            
            assert response.status_code == 500
            error_data = response.json()
            assert "Failed to initiate novelty assessment" in error_data["detail"]

    def test_invalid_request_validation(self):
        """Test request validation and error responses"""
        
        # Test missing required fields
        invalid_request = {
            "research_title": "Test Title"
            # Missing abstract and claims
        }
        
        response = client.post("/api/novelty/assess", json=invalid_request)
        assert response.status_code == 422  # Validation error
        
        # Test invalid data types
        invalid_request = {
            "research_title": 123,  # Should be string
            "research_abstract": "Valid abstract",
            "claims": "Should be list"  # Should be list
        }
        
        response = client.post("/api/novelty/assess", json=invalid_request)
        assert response.status_code == 422

    def test_assessment_not_found_handling(self):
        """Test handling of non-existent assessment IDs"""
        
        with patch.object(NoveltyAssessmentService, 'get_assessment_result') as mock_get:
            mock_get.return_value = None
            
            response = client.get("/api/novelty/results/non-existent-id")
            
            assert response.status_code == 404
            error_data = response.json()
            assert "not found" in error_data["detail"]

    def test_concurrent_assessments(self, sample_assessment_request):
        """Test handling of concurrent assessment requests"""
        
        with patch.object(NoveltyAssessmentService, 'assess_novelty') as mock_assess:
            # Simulate multiple concurrent requests
            mock_assess.side_effect = [
                {"assessment_id": "concurrent-1", "status": "processing", "message": "Assessment 1 started"},
                {"assessment_id": "concurrent-2", "status": "processing", "message": "Assessment 2 started"},
                {"assessment_id": "concurrent-3", "status": "processing", "message": "Assessment 3 started"}
            ]
            
            # Submit multiple requests
            responses = []
            for i in range(3):
                request_data = sample_assessment_request.copy()
                request_data["user_id"] = f"user-{i}"
                response = client.post("/api/novelty/assess", json=request_data)
                responses.append(response)
            
            # Verify all requests succeeded
            for i, response in enumerate(responses):
                assert response.status_code == 200
                data = response.json()
                assert data["assessment_id"] == f"concurrent-{i+1}"
                assert data["status"] == "processing"

    def test_health_check_integration(self):
        """Test health check endpoint integration"""
        
        response = client.get("/api/novelty/health")
        
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert health_data["service"] == "novelty-assessment"
        assert "capabilities" in health_data
        assert "novelty_assessment" in health_data["capabilities"]

    def test_performance_with_large_datasets(self, sample_assessment_request):
        """Test performance with large claim sets and prior art"""
        
        # Create request with many claims
        large_request = sample_assessment_request.copy()
        large_request["claims"] = [f"Claim {i}: A method for processing data using technique {i}" for i in range(50)]
        
        with patch.object(NoveltyAssessmentService, 'assess_novelty') as mock_assess:
            mock_assess.return_value = {
                "assessment_id": "large-assessment-123",
                "status": "processing",
                "message": "Large assessment initiated"
            }
            
            response = client.post("/api/novelty/assess", json=large_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["assessment_id"] == "large-assessment-123"
            
            # Verify service was called with large dataset
            mock_assess.assert_called_once()
            call_args = mock_assess.call_args
            assert len(call_args[1]["claims"]) == 50

    def test_data_persistence_integration(self, sample_assessment_request, mock_assessment_result):
        """Test data persistence across requests"""
        
        with patch.object(NoveltyAssessmentService, 'assess_novelty') as mock_assess, \
             patch.object(NoveltyAssessmentService, 'get_assessment_result') as mock_get_result:
            
            # Setup mocks
            mock_assess.return_value = {
                "assessment_id": "persistent-assessment-456",
                "status": "processing",
                "message": "Assessment initiated"
            }
            
            mock_get_result.return_value = mock_assessment_result
            
            # Submit assessment
            response1 = client.post("/api/novelty/assess", json=sample_assessment_request)
            assert response1.status_code == 200
            assessment_id = response1.json()["assessment_id"]
            
            # Retrieve results multiple times
            for _ in range(3):
                response2 = client.get(f"/api/novelty/results/{assessment_id}")
                assert response2.status_code == 200
                result_data = response2.json()
                assert result_data["assessment_id"] == assessment_id
                assert result_data["status"] == "completed"
"""
Unit tests for Novelty Assessment Service

Tests the comprehensive novelty assessment functionality including
prior art search, similarity analysis, and report generation.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import uuid

from src.services.novelty_assessment_service import NoveltyAssessmentService
from src.agents.enhanced_novelty import NoveltyAssessment


class TestNoveltyAssessmentService:
    """Test suite for NoveltyAssessmentService"""
    
    @pytest.fixture
    def service(self):
        """Create a NoveltyAssessmentService instance for testing"""
        return NoveltyAssessmentService()
    
    @pytest.fixture
    def sample_assessment_data(self):
        """Sample assessment data for testing"""
        return {
            "research_title": "Quantum Computing Algorithm for Optimization",
            "research_abstract": "A novel quantum algorithm that improves optimization performance",
            "claims": [
                "A quantum computing method for solving optimization problems",
                "The method uses quantum superposition to explore solution space"
            ]
        }
    
    @pytest.fixture
    def mock_novelty_assessment(self):
        """Mock NoveltyAssessment result"""
        return NoveltyAssessment(
            overall_novelty_score=0.85,
            novelty_category="Highly Novel",
            similar_patents=[
                {
                    "id": "US123456",
                    "title": "Quantum Optimization Method",
                    "similarity_score": 0.65,
                    "publication_date": "2023-01-15"
                }
            ],
            similar_publications=[
                {
                    "id": "pub123",
                    "title": "Quantum Algorithms for Optimization",
                    "similarity_score": 0.72,
                    "publication_date": "2023-03-20"
                }
            ],
            key_differences=[
                "Novel quantum superposition approach",
                "Improved convergence algorithm"
            ],
            patentability_indicators={
                "novelty_score": 0.85,
                "patentability_likelihood": "High",
                "prior_art_conflicts": 0
            },
            prior_art_analysis={
                "total_similar_patents": 1,
                "total_similar_publications": 1,
                "highest_patent_similarity": 0.65,
                "highest_publication_similarity": 0.72
            },
            recommendations=[
                "Strong novelty detected - proceed with patent application",
                "Conduct professional prior art search before filing"
            ]
        )
    
    @pytest.mark.asyncio
    async def test_assess_novelty_initiation(self, service, sample_assessment_data):
        """Test novelty assessment initiation"""
        result = await service.assess_novelty(
            research_title=sample_assessment_data["research_title"],
            research_abstract=sample_assessment_data["research_abstract"],
            claims=sample_assessment_data["claims"],
            user_id="test_user"
        )
        
        # Check response structure
        assert "assessment_id" in result
        assert result["status"] == "processing"
        assert "message" in result
        
        # Verify assessment is stored
        assessment_id = result["assessment_id"]
        stored_assessment = service.assessments.get(assessment_id)
        assert stored_assessment is not None
        assert stored_assessment["research_title"] == sample_assessment_data["research_title"]
        assert stored_assessment["status"] == "processing"
    
    @pytest.mark.asyncio
    async def test_get_assessment_result_not_found(self, service):
        """Test getting assessment result for non-existent ID"""
        result = await service.get_assessment_result("non-existent-id")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_assessment_result_processing(self, service, sample_assessment_data):
        """Test getting assessment result while processing"""
        # Start assessment
        result = await service.assess_novelty(
            research_title=sample_assessment_data["research_title"],
            research_abstract=sample_assessment_data["research_abstract"],
            claims=sample_assessment_data["claims"]
        )
        assessment_id = result["assessment_id"]
        
        # Get result immediately (should be processing)
        assessment_result = await service.get_assessment_result(assessment_id)
        assert assessment_result["status"] == "processing"
        assert assessment_result["assessment"] is None
    
    @pytest.mark.asyncio
    @patch('src.services.novelty_assessment_service.search_similar_patents_publications')
    @patch.object(NoveltyAssessmentService, '_search_similar_patents')
    @patch.object(NoveltyAssessmentService, '_search_similar_publications')
    async def test_process_assessment_success(
        self, 
        mock_search_pubs, 
        mock_search_patents, 
        mock_search_api,
        service, 
        sample_assessment_data, 
        mock_novelty_assessment
    ):
        """Test successful assessment processing"""
        # Mock search results
        mock_search_patents.return_value = [
            {"id": "US123456", "title": "Test Patent", "abstract": "Test abstract"}
        ]
        mock_search_pubs.return_value = [
            {"id": "pub123", "title": "Test Publication", "abstract": "Test abstract"}
        ]
        
        # Mock novelty assessor
        with patch.object(service.novelty_assessor, 'assess_novelty', return_value=mock_novelty_assessment):
            # Start assessment
            result = await service.assess_novelty(
                research_title=sample_assessment_data["research_title"],
                research_abstract=sample_assessment_data["research_abstract"],
                claims=sample_assessment_data["claims"]
            )
            assessment_id = result["assessment_id"]
            
            # Wait for processing to complete
            await asyncio.sleep(0.1)  # Give background task time to run
            
            # Check final result
            assessment_result = await service.get_assessment_result(assessment_id)
            assert assessment_result["status"] == "completed"
            assert assessment_result["assessment"] is not None
            assert assessment_result["assessment"]["overall_novelty_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_compare_claims(self, service):
        """Test claim comparison functionality"""
        research_claims = [
            "A quantum computing method for optimization",
            "The method uses quantum superposition"
        ]
        patent_claims = [
            "A classical optimization algorithm",
            "The algorithm uses iterative improvement"
        ]
        
        with patch.object(service.novelty_assessor.model, 'encode') as mock_encode:
            # Mock embeddings
            mock_encode.side_effect = [
                [[0.1, 0.2, 0.3]],  # research_text embedding
                [[0.4, 0.5, 0.6]],  # patent_text embedding
                [[0.1, 0.2, 0.3]],  # research_claim_1 embedding
                [[0.4, 0.5, 0.6]],  # patent_claim_1 embedding
                [[0.7, 0.8, 0.9]],  # patent_claim_2 embedding
                [[0.2, 0.3, 0.4]],  # research_claim_2 embedding
                [[0.4, 0.5, 0.6]],  # patent_claim_1 embedding (again)
                [[0.7, 0.8, 0.9]]   # patent_claim_2 embedding (again)
            ]
            
            result = await service.compare_claims(
                research_claims=research_claims,
                patent_claims=patent_claims,
                patent_id="US123456"
            )
            
            assert result["patent_id"] == "US123456"
            assert "overall_similarity" in result
            assert "conflict_assessment" in result
            assert "claim_comparisons" in result
            assert len(result["claim_comparisons"]) == 2
            assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_compare_claims_error_handling(self, service):
        """Test claim comparison error handling"""
        with patch.object(service.novelty_assessor.model, 'encode', side_effect=Exception("Model error")):
            result = await service.compare_claims(
                research_claims=["test claim"],
                patent_claims=["test patent claim"],
                patent_id="US123456"
            )
            
            assert "error" in result
            assert result["patent_id"] == "US123456"
    
    @pytest.mark.asyncio
    async def test_generate_assessment_report_not_found(self, service):
        """Test report generation for non-existent assessment"""
        result = await service.generate_assessment_report("non-existent-id")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_generate_assessment_report_not_completed(self, service, sample_assessment_data):
        """Test report generation for incomplete assessment"""
        # Start assessment but don't complete it
        result = await service.assess_novelty(
            research_title=sample_assessment_data["research_title"],
            research_abstract=sample_assessment_data["research_abstract"],
            claims=sample_assessment_data["claims"]
        )
        assessment_id = result["assessment_id"]
        
        # Try to generate report
        report_result = await service.generate_assessment_report(assessment_id)
        assert report_result is None
    
    @pytest.mark.asyncio
    async def test_generate_assessment_report_success(self, service, mock_novelty_assessment):
        """Test successful report generation"""
        # Create a completed assessment
        assessment_id = str(uuid.uuid4())
        service.assessments[assessment_id] = {
            "id": assessment_id,
            "research_title": "Test Research",
            "research_abstract": "Test abstract",
            "claims": ["Test claim"],
            "status": "completed",
            "assessment": {
                "overall_novelty_score": 0.85,
                "novelty_category": "Highly Novel",
                "patentability_indicators": {
                    "patentability_likelihood": "High",
                    "prior_art_conflicts": 0
                },
                "recommendations": ["Test recommendation"]
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Mock report generator
        mock_report = {
            "title": "Test Report",
            "report_content": "Generated report content"
        }
        
        with patch.object(service.report_generator, 'generate_comprehensive_report', return_value=mock_report):
            result = await service.generate_assessment_report(assessment_id, include_detailed_analysis=True)
            
            assert result is not None
            assert result["assessment_id"] == assessment_id
            assert "assessment_summary" in result
            assert result["assessment_summary"]["novelty_score"] == 0.85
            assert result["detailed_report"] == mock_report
    
    @pytest.mark.asyncio
    async def test_get_user_assessments(self, service):
        """Test getting user assessments"""
        user_id = "test_user"
        
        # Create some assessments for the user
        assessment1_id = str(uuid.uuid4())
        assessment2_id = str(uuid.uuid4())
        other_user_id = str(uuid.uuid4())
        
        service.assessments[assessment1_id] = {
            "id": assessment1_id,
            "research_title": "Research 1",
            "user_id": user_id,
            "status": "completed",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T01:00:00"
        }
        
        service.assessments[assessment2_id] = {
            "id": assessment2_id,
            "research_title": "Research 2",
            "user_id": user_id,
            "status": "processing",
            "created_at": "2024-01-02T00:00:00",
            "updated_at": "2024-01-02T00:30:00"
        }
        
        service.assessments[other_user_id] = {
            "id": other_user_id,
            "research_title": "Other Research",
            "user_id": "other_user",
            "status": "completed",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T01:00:00"
        }
        
        # Get user assessments
        user_assessments = await service.get_user_assessments(user_id)
        
        assert len(user_assessments) == 2
        assert all(assessment["user_id"] == user_id for assessment in user_assessments if "user_id" in assessment)
        # Should be sorted by created_at descending
        assert user_assessments[0]["created_at"] >= user_assessments[1]["created_at"]
    
    @pytest.mark.asyncio
    @patch('src.services.novelty_assessment_service.search_similar_patents_publications')
    async def test_search_similar_patents(self, mock_search, service):
        """Test patent search functionality"""
        mock_search.return_value = {
            "patents": [
                {"id": "US123456", "title": "Test Patent", "abstract": "Test abstract"}
            ]
        }
        
        with patch('src.services.novelty_assessment_service.fetch_patent_metadata', return_value={"assignee": "Test Corp"}):
            result = await service._search_similar_patents("Test Title", "Test Abstract")
            
            assert len(result) == 1
            assert result[0]["id"] == "US123456"
            assert result[0]["assignee"] == "Test Corp"
    
    @pytest.mark.asyncio
    @patch('src.services.novelty_assessment_service.search_similar_patents_publications')
    async def test_search_similar_publications(self, mock_search, service):
        """Test publication search functionality"""
        mock_search.return_value = {
            "publications": [
                {"id": "pub123", "title": "Test Publication", "abstract": "Test abstract"}
            ]
        }
        
        with patch('src.services.novelty_assessment_service.fetch_publication_metadata', return_value={"journal": "Test Journal"}):
            result = await service._search_similar_publications("Test Title", "Test Abstract")
            
            assert len(result) == 1
            assert result[0]["id"] == "pub123"
            assert result[0]["journal"] == "Test Journal"
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self, service):
        """Test search error handling"""
        with patch('src.services.novelty_assessment_service.search_similar_patents_publications', side_effect=Exception("API Error")):
            patents = await service._search_similar_patents("Test", "Test")
            publications = await service._search_similar_publications("Test", "Test")
            
            assert patents == []
            assert publications == []
    
    def test_generate_claim_recommendations(self, service):
        """Test claim recommendation generation"""
        claim_comparisons = [
            {"conflict_risk": "High", "similarity_score": 0.9},
            {"conflict_risk": "Medium", "similarity_score": 0.7},
            {"conflict_risk": "Low", "similarity_score": 0.3}
        ]
        
        # High similarity case
        recommendations = service._generate_claim_recommendations(0.85, claim_comparisons)
        assert any("High overall similarity" in rec for rec in recommendations)
        assert any("1 claims have high conflict risk" in rec for rec in recommendations)
        assert any("1 claims have medium conflict risk" in rec for rec in recommendations)
        
        # Low similarity case
        recommendations = service._generate_claim_recommendations(0.3, [])
        assert any("low conflict risk" in rec for rec in recommendations)


class TestNoveltyAssessmentIntegration:
    """Integration tests for novelty assessment functionality"""
    
    @pytest.mark.asyncio
    async def test_full_assessment_workflow(self):
        """Test complete assessment workflow from start to finish"""
        service = NoveltyAssessmentService()
        
        # Mock all external dependencies
        with patch.object(service, '_search_similar_patents', return_value=[]), \
             patch.object(service, '_search_similar_publications', return_value=[]), \
             patch.object(service.novelty_assessor, 'assess_novelty') as mock_assess:
            
            # Mock assessment result
            mock_assess.return_value = NoveltyAssessment(
                overall_novelty_score=0.8,
                novelty_category="Highly Novel",
                similar_patents=[],
                similar_publications=[],
                key_differences=["Novel approach"],
                patentability_indicators={"patentability_likelihood": "High"},
                prior_art_analysis={"total_similar_patents": 0},
                recommendations=["Proceed with patent application"]
            )
            
            # Start assessment
            result = await service.assess_novelty(
                research_title="Test Research",
                research_abstract="Test abstract",
                claims=["Test claim"],
                user_id="test_user"
            )
            
            assessment_id = result["assessment_id"]
            
            # Wait for processing
            await asyncio.sleep(0.1)
            
            # Check final result
            final_result = await service.get_assessment_result(assessment_id)
            assert final_result["status"] == "completed"
            assert final_result["assessment"]["overall_novelty_score"] == 0.8
            
            # Generate report
            with patch.object(service.report_generator, 'generate_comprehensive_report', return_value={"title": "Test Report"}):
                report = await service.generate_assessment_report(assessment_id)
                assert report is not None
                assert report["assessment_summary"]["novelty_score"] == 0.8


if __name__ == "__main__":
    pytest.main([__file__])
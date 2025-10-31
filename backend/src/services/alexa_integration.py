import boto3
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
import logging

class AlexaDataIntegration:
    def __init__(self, aws_access_key: str = None, aws_secret_key: str = None, region: str = 'us-east-1'):
        """Initialize Alexa integration service"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize AWS clients
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        # Initialize services
        self.comprehend = self.session.client('comprehend')
        self.transcribe = self.session.client('transcribe')
        self.s3 = self.session.client('s3')
        
    async def process_voice_query(
        self, 
        audio_file_path: str,
        research_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process voice queries about patent alerts and research
        """
        try:
            # Transcribe audio to text
            transcription = await self._transcribe_audio(audio_file_path)
            
            # Extract intent and entities
            intent_analysis = await self._analyze_intent(transcription)
            
            # Process based on intent
            response = await self._process_intent(
                intent_analysis, 
                transcription, 
                research_context
            )
            
            return {
                'transcription': transcription,
                'intent': intent_analysis,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing voice query: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text"""
        try:
            # Upload audio to S3 temporarily
            bucket_name = 'patent-alerts-temp'
            object_name = f"audio_{datetime.now().timestamp()}.wav"
            
            self.s3.upload_file(audio_file_path, bucket_name, object_name)
            
            # Start transcription job
            job_name = f"transcription_{datetime.now().timestamp()}"
            
            response = self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f's3://{bucket_name}/{object_name}'},
                MediaFormat='wav',
                LanguageCode='en-US'
            )
            
            # Wait for completion (simplified - would use async polling in production)
            import time
            time.sleep(10)
            
            # Get results
            result = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            transcript_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # Download and parse transcript
            # This is simplified - would need proper URI handling
            return "Mock transcription: Tell me about recent patents in quantum computing"
            
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return "Error in transcription"
    
    async def _analyze_intent(self, text: str) -> Dict[str, Any]:
        """Analyze intent from transcribed text"""
        try:
            # Use AWS Comprehend for entity detection
            entities_response = self.comprehend.detect_entities(
                Text=text,
                LanguageCode='en'
            )
            
            # Simple intent classification
            intents = {
                'search_patents': ['patent', 'patents', 'find', 'search'],
                'get_alerts': ['alert', 'alerts', 'notify', 'notification'],
                'analyze_novelty': ['novel', 'novelty', 'new', 'unique'],
                'find_competitors': ['competitor', 'competitors', 'competition'],
                'licensing_opportunities': ['license', 'licensing', 'opportunity']
            }
            
            detected_intent = 'unknown'
            confidence = 0.0
            
            text_lower = text.lower()
            for intent, keywords in intents.items():
                matches = sum(1 for keyword in keywords if keyword in text_lower)
                intent_confidence = matches / len(keywords)
                
                if intent_confidence > confidence:
                    confidence = intent_confidence
                    detected_intent = intent
            
            return {
                'intent': detected_intent,
                'confidence': confidence,
                'entities': entities_response.get('Entities', []),
                'original_text': text
            }
            
        except Exception as e:
            self.logger.error(f"Intent analysis error: {e}")
            return {'intent': 'unknown', 'confidence': 0.0, 'entities': []}
    
    async def _process_intent(
        self,
        intent_analysis: Dict[str, Any],
        original_text: str,
        research_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process the detected intent and generate response"""
        intent = intent_analysis['intent']
        
        if intent == 'search_patents':
            return await self._handle_patent_search(original_text, research_context)
        elif intent == 'get_alerts':
            return await self._handle_alert_request(original_text, research_context)
        elif intent == 'analyze_novelty':
            return await self._handle_novelty_analysis(original_text, research_context)
        elif intent == 'find_competitors':
            return await self._handle_competitor_search(original_text, research_context)
        elif intent == 'licensing_opportunities':
            return await self._handle_licensing_search(original_text, research_context)
        else:
            return {
                'response_type': 'clarification',
                'message': "I'm not sure what you're looking for. Could you please rephrase your question?",
                'suggestions': [
                    "Search for patents",
                    "Get patent alerts",
                    "Analyze novelty",
                    "Find competitors",
                    "Find licensing opportunities"
                ]
            }
    
    async def _handle_patent_search(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle patent search requests"""
        # Extract search terms from query
        search_terms = self._extract_search_terms(query)
        
        # This would integrate with your existing search logic
        return {
            'response_type': 'patent_search',
            'message': f"Searching for patents related to: {', '.join(search_terms)}",
            'search_terms': search_terms,
            'action': 'perform_patent_search'
        }
    
    async def _handle_alert_request(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle alert requests"""
        return {
            'response_type': 'alerts',
            'message': "Here are your recent patent alerts",
            'action': 'get_recent_alerts'
        }
    
    async def _handle_novelty_analysis(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle novelty analysis requests"""
        return {
            'response_type': 'novelty_analysis',
            'message': "Analyzing novelty of your research",
            'action': 'perform_novelty_analysis'
        }
    
    async def _handle_competitor_search(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle competitor search requests"""
        return {
            'response_type': 'competitor_search',
            'message': "Searching for competitors in your research domain",
            'action': 'find_competitors'
        }
    
    async def _handle_licensing_search(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle licensing opportunity requests"""
        return {
            'response_type': 'licensing_search',
            'message': "Identifying licensing opportunities",
            'action': 'find_licensing_opportunities'
        }
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from natural language query"""
        # Simple term extraction - would be enhanced with NLP
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [word.lower().strip('.,!?') for word in query.split()]
        return [word for word in words if word not in stop_words and len(word) > 2]

    async def create_voice_response(self, response_data: Dict[str, Any]) -> str:
        """Create voice-friendly response"""
        response_type = response_data.get('response_type', 'unknown')
        
        if response_type == 'patent_search':
            return f"I found several patents related to your search. The most relevant ones are in {response_data.get('domain', 'your research area')}."
        elif response_type == 'alerts':
            alert_count = response_data.get('alert_count', 0)
            return f"You have {alert_count} new patent alerts. Would you like me to summarize them?"
        elif response_type == 'novelty_analysis':
            novelty_score = response_data.get('novelty_score', 0)
            return f"Your research shows a novelty score of {novelty_score:.1f} out of 1.0. This indicates {response_data.get('novelty_category', 'moderate')} novelty."
        else:
            return "I've processed your request. You can view the detailed results in your dashboard." 
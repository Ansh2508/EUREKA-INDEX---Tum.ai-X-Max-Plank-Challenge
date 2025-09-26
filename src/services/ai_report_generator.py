import os
import anthropic
from typing import Dict, Any, List
from dotenv import load_dotenv
# Web search now handled directly by Claude Opus 4.1

load_dotenv()

class AIReportGenerator:
    """Generate comprehensive AI-powered reports using Claude and web search"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
            
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Use Claude Opus 4.1 for advanced analysis
        self.model = "claude-opus-4-1"
    
    async def generate_comprehensive_report(
        self, 
        analysis_data: Dict[str, Any], 
        title: str, 
        abstract: str
    ) -> Dict[str, Any]:
        """Generate a comprehensive technology transfer report"""
        
        # Generate comprehensive report with Claude Opus 4.1 including web search
        report_content = await self._generate_report_with_claude_web_search(
            analysis_data, title, abstract
        )
        
        return {
            "title": f"Technology Transfer Report: {title}",
            "generated_at": "2024",
            "report_content": report_content,
            "analysis_data": analysis_data,
            "current_market_info": "Integrated via Claude web search",
            "methodology": "AI-generated report using Claude Opus 4.1 with integrated web search"
        }
    
# Web search methods removed - now handled directly by Claude Opus 4.1
    
    async def _generate_report_with_claude_web_search(
        self, 
        analysis_data: Dict[str, Any], 
        title: str, 
        abstract: str
    ) -> str:
        """Generate comprehensive report using Claude Opus 4.1 with web search"""
        
        # Create comprehensive prompt with web search instructions
        prompt = f"""You are a senior technology transfer analyst at a prestigious research institution. I need you to generate a comprehensive, professional technology transfer report based on the provided analysis data and current web research.

**RESEARCH TECHNOLOGY:**
Title: {title}
Abstract: {abstract}

**QUANTITATIVE ANALYSIS DATA:**
{self._format_analysis_data(analysis_data)}

**INSTRUCTIONS:**
First, please search the web for current information about:
1. Recent developments in "{title}" technology in 2024
2. Market trends for "{title}" industry 2024
3. Patent landscape and competitive analysis for "{title}"
4. Investment and funding activity in "{title}" sector
5. Regulatory developments affecting "{title}" technology

Then, generate a detailed, professional report with the following sections:

1. **Executive Summary** (2-3 paragraphs)
   - Key findings and recommendations based on current data
   - Market potential assessment with 2024 context
   - Commercial viability conclusion

2. **Technology Assessment** (detailed analysis)
   - Technology readiness level interpretation
   - Competitive advantages identified from current market research
   - Technical barriers and risks with current market context

3. **Market Analysis** (comprehensive market evaluation)
   - Current market landscape and 2024 trends from web research
   - Target markets and applications
   - Market size and growth potential with recent data
   - Competitive positioning analysis

4. **Commercial Indicators Analysis**
   - Patent landscape interpretation with current activity
   - Citation analysis insights
   - Geographic market penetration trends
   - Investment attractiveness based on recent funding data

5. **Strategic Recommendations**
   - Licensing opportunities identified from current market gaps
   - Partnership strategies based on current industry players
   - Risk mitigation approaches considering 2024 market conditions
   - Timeline for commercialization with current market readiness

6. **Current Market Context** (based on 2024 web research)
   - Recent developments and announcements
   - Market dynamics and emerging trends
   - Regulatory environment changes
   - Investment climate and funding patterns

**STYLE REQUIREMENTS:**
- Professional, analytical tone
- Data-driven insights incorporating both analysis data and web research
- Specific, actionable recommendations
- Clear structure with headings
- Executive-level language
- 1500-2000 words
- Reference current market information throughout

Please conduct web searches first, then generate the comprehensive report incorporating both the quantitative analysis and current market intelligence."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more focused, professional output
                tools=[
                    {
                        "type": "web_search",
                        "web_search": {
                            "description": "Search the web for current information about technology trends, market data, and industry developments"
                        }
                    }
                ],
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            # Fallback to regular Claude without web search if web search fails
            return await self._generate_report_fallback(analysis_data, title, abstract, str(e))
    
    async def _generate_report_fallback(
        self, 
        analysis_data: Dict[str, Any], 
        title: str, 
        abstract: str,
        error_msg: str
    ) -> str:
        """Fallback report generation without web search"""
        
        prompt = f"""You are a senior technology transfer analyst. Generate a comprehensive technology transfer report based on the provided analysis data.

**RESEARCH TECHNOLOGY:**
Title: {title}
Abstract: {abstract}

**QUANTITATIVE ANALYSIS DATA:**
{self._format_analysis_data(analysis_data)}

**NOTE:** Web search functionality is currently unavailable ({error_msg}). Please generate the report based on the provided quantitative analysis and your knowledge base.

Generate a detailed, professional report with:
1. Executive Summary
2. Technology Assessment  
3. Market Analysis
4. Commercial Indicators Analysis
5. Strategic Recommendations

**STYLE:** Professional, analytical tone with 1200-1500 words."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating report (fallback): {str(e)}. Please ensure ANTHROPIC_API_KEY is properly configured."
    
    def _format_analysis_data(self, data: Dict[str, Any]) -> str:
        """Format analysis data for the prompt"""
        try:
            overall = data.get("overall_assessment", {})
            market = data.get("market_analysis", {})
            technology = data.get("technology_assessment", {})
            commercial = data.get("commercial_indicators", {})
            
            return f"""
Overall Assessment:
- Market Potential Score: {overall.get('market_potential_score', 'N/A')}
- Investment Recommendation: {overall.get('investment_recommendation', 'N/A')}
- Risk Level: {overall.get('risk_level', 'N/A')}

Market Analysis:
- Gap Status: {market.get('gap_status', 'N/A')}
- Gap Score: {market.get('gap_score', 'N/A')}
- Need Indicators: {market.get('need_indicators', 'N/A')}
- Solution Indicators: {market.get('solution_indicators', 'N/A')}
- Publication Momentum: {market.get('publication_momentum', 'N/A')}
- Patent Density: {market.get('patent_density', 'N/A')}

Technology Assessment:
- Technology Readiness Level: {technology.get('estimated_trl', 'N/A')}
- TRL Category: {technology.get('trl_category', 'N/A')}
- Market Readiness: {technology.get('market_readiness', 'N/A')}
- Time to Market: {technology.get('time_to_market', 'N/A')}

Commercial Indicators:
- Citation Velocity: {commercial.get('citation_velocity', 'N/A')}
- Commercial Ratio: {commercial.get('commercial_ratio', 'N/A')}
- Average Family Size: {commercial.get('avg_family_size', 'N/A')}
- Geographic Diversity: {commercial.get('geographic_diversity', 'N/A')}
"""
        except Exception as e:
            return f"Error formatting analysis data: {str(e)}"
    
# Current info formatting removed - now handled by Claude web search

def main():
    """Test the AI report generator"""
    # Mock analysis data for testing
    test_data = {
        "overall_assessment": {
            "market_potential_score": 7.5,
            "investment_recommendation": "CONSIDER - Moderate commercial potential",
            "risk_level": "Medium"
        },
        "market_analysis": {
            "gap_status": "CLEAR_MARKET_GAP_IDENTIFIED",
            "gap_score": 8.2,
            "need_indicators": 15,
            "solution_indicators": 12,
            "publication_momentum": "High",
            "patent_density": 0.45
        },
        "technology_assessment": {
            "estimated_trl": 7,
            "trl_category": "SYSTEM_PROTOTYPE",
            "market_readiness": "Near Market",
            "time_to_market": "2-3 years"
        },
        "commercial_indicators": {
            "citation_velocity": 2.3,
            "commercial_ratio": 0.35,
            "avg_family_size": 4.2,
            "geographic_diversity": 0.67
        }
    }
    
    generator = AIReportGenerator()
    
    import asyncio
    async def test():
        report = await generator.generate_comprehensive_report(
            test_data,
            "QuantumScape Solid-State Battery Technology",
            "Advanced solid-state lithium battery technology with enhanced energy density and safety features."
        )
        print("Generated Report:")
        print("=" * 50)
        print(report["report_content"])
    
    asyncio.run(test())

if __name__ == "__main__":
    main()

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_AI_API_KEY")

def get_google_ai_response(prompt: str, model: str = "gemini-2.5-pro", max_tokens: int = 2048, temperature: float = 0.3) -> str:
    """
    OPTIMIZED Google AI (Gemini) for maximum performance and quality
    
    Available models (ordered by capability):
    - gemini-2.5-pro (BEST - most capable, detailed analysis)
    - gemini-2.5-flash (fast, good quality)
    - gemini-flash-latest (latest version)
    
    Optimizations applied:
    - Enhanced system prompt for expert-level responses
    - Optimized temperature for balanced creativity/accuracy
    - Higher token limit for detailed responses
    - Advanced generation settings
    """
    
    if not API_KEY:
        return "Error: GOOGLE_AI_API_KEY not set in environment"
    
    try:
        # Configure the API key
        genai.configure(api_key=API_KEY)
        
        # ENHANCED SYSTEM PROMPT for expert-level responses
        enhanced_prompt = f"""As a world-class expert in technology and innovation, provide a comprehensive analysis of the following:

{prompt}

Structure your response with clear sections and provide specific, actionable insights."""
        
        # Create the model with system instructions
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction="You are a world-class expert in patent analysis, technology assessment, and innovation research. Provide detailed, comprehensive, and actionable insights with specific examples and clear structure."
        )
        
        # ZERO safety restrictions for maximum capability
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        # OPTIMIZED generation settings for best quality
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,  # Lower for more focused, accurate responses
            top_p=0.95,              # High diversity in token selection
            top_k=40,                # Balanced creativity
            candidate_count=1,       # Single best response
            stop_sequences=None      # No early stopping
        )
        
        # Generate enhanced response
        response = model_instance.generate_content(
            enhanced_prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Handle response with safety check fallback
        if hasattr(response, 'text') and response.text:
            return response.text
        elif response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content.parts:
                return candidate.content.parts[0].text
        
        # If all else fails, return a helpful message
        return "Response could not be generated due to content restrictions. Please try rephrasing your question."
        
    except Exception as e:
        # Fallback to simpler prompt if enhanced version fails
        try:
            genai.configure(api_key=API_KEY)
            simple_model = genai.GenerativeModel("gemini-2.5-flash")
            
            fallback_response = simple_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                ),
                safety_settings=safety_settings
            )
            return fallback_response.text
        except:
            return f"Error: {str(e)}"

def get_patent_analysis(patent_text: str, analysis_type: str = "novelty") -> str:
    """
    Specialized function for patent analysis with expert prompting
    
    analysis_type options:
    - novelty: Assess novelty and prior art
    - claims: Analyze patent claims structure
    - landscape: Technology landscape analysis
    - infringement: Infringement risk assessment
    """
    
    analysis_prompts = {
        "novelty": f"""As a patent examiner with 15+ years of experience, conduct a comprehensive novelty analysis of this patent/invention:

{patent_text}

Provide:
1. **Novelty Assessment**: Key innovative elements
2. **Prior Art Concerns**: Potential conflicts and search strategies  
3. **Patentability Score**: Rate 1-10 with justification
4. **Claim Recommendations**: How to strengthen the application
5. **Risk Mitigation**: Strategies to overcome rejections""",

        "claims": f"""As a patent attorney specializing in claim drafting, analyze these patent claims:

{patent_text}

Provide:
1. **Claim Structure Analysis**: Independent vs dependent claims
2. **Scope Assessment**: Breadth and limitations
3. **Vulnerability Analysis**: Potential design-around strategies
4. **Strengthening Recommendations**: Additional claims to file
5. **Prosecution Strategy**: Anticipated examiner objections""",

        "landscape": f"""As a technology intelligence analyst, provide a comprehensive landscape analysis for this technology:

{patent_text}

Provide:
1. **Market Position**: Where this fits in the competitive landscape
2. **Key Players**: Major patent holders and competitors
3. **White Space Analysis**: Opportunities for innovation
4. **Trend Analysis**: Technology evolution and future directions
5. **Strategic Recommendations**: IP strategy and R&D focus areas""",

        "infringement": f"""As an IP litigation expert, assess potential infringement risks for this technology:

{patent_text}

Provide:
1. **Infringement Risk Assessment**: Likelihood and severity
2. **Key Patents of Concern**: Specific patents that may be infringed
3. **Design-Around Options**: Alternative implementations
4. **Freedom to Operate**: Overall FTO assessment
5. **Mitigation Strategies**: Legal and technical approaches"""
    }
    
    selected_prompt = analysis_prompts.get(analysis_type, analysis_prompts["novelty"])
    return get_google_ai_response(selected_prompt, max_tokens=3000, temperature=0.2)

def get_technical_innovation_analysis(technology_description: str) -> str:
    """
    Specialized function for analyzing technical innovations
    """
    
    prompt = f"""As a senior technology analyst and innovation expert, provide a comprehensive technical analysis:

Technology Description:
{technology_description}

Provide detailed analysis covering:

## 1. Technical Merit Assessment
- Core innovation and technical advantages
- Comparison with existing solutions
- Technical feasibility and maturity level

## 2. Intellectual Property Landscape
- Patentability assessment
- Prior art landscape
- IP strategy recommendations

## 3. Market and Commercial Potential
- Target markets and applications
- Competitive advantages
- Commercialization challenges

## 4. Development Roadmap
- Technical milestones and timeline
- Resource requirements
- Risk factors and mitigation

## 5. Strategic Recommendations
- Next steps for development
- Partnership opportunities
- Investment considerations

Provide specific, actionable insights with concrete examples and data where possible."""

    return get_google_ai_response(prompt, max_tokens=4000, temperature=0.25)

def get_prior_art_search_strategy(invention_summary: str) -> str:
    """
    Generate comprehensive prior art search strategy
    """
    
    prompt = f"""As a professional patent searcher with expertise in multiple technical domains, create a comprehensive prior art search strategy:

Invention Summary:
{invention_summary}

Provide a detailed search strategy including:

## 1. Search Scope Definition
- Key technical concepts and terminology
- Classification codes (CPC, IPC, USPC)
- Time frame and geographical scope

## 2. Database Strategy
- Primary patent databases to search
- Non-patent literature sources
- Academic and technical databases

## 3. Search Query Development
- Boolean search strings
- Keyword variations and synonyms
- Classification-based searches

## 4. Search Execution Plan
- Search sequence and methodology
- Iterative refinement approach
- Quality control measures

## 5. Analysis Framework
- Relevance assessment criteria
- Documentation requirements
- Reporting structure

Include specific search strings, database recommendations, and expected timeline."""

    return get_google_ai_response(prompt, max_tokens=3500, temperature=0.2)

def main():
    # Test the enhanced system
    test_prompt = "Analyze the patentability of a machine learning system that predicts drug-target interactions using graph neural networks."
    
    print("=== TESTING ENHANCED GOOGLE AI ===")
    print("Question:", test_prompt)
    print("\n" + "="*60)
    
    answer = get_google_ai_response(test_prompt, max_tokens=2000)
    print("Enhanced Response:")
    print(answer)
    
    print("\n" + "="*60)
    print("✅ Enhanced Google AI system is ready!")

if __name__ == "__main__":
    main()
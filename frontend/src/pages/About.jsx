import {
    Code,
    Database,
    Zap,
    Shield,
    Globe,
    Cpu,
    Brain,
    Search,
    BarChart3,
    FileText,
    Bell,
    Users,
    Target,
    Lightbulb,
    Rocket,
    CheckCircle
} from 'lucide-react'
import './About.css'

function About() {
    const techStack = {
        frontend: [
            { name: 'React 18', description: 'Modern UI library with hooks and concurrent features' },
            { name: 'Vite', description: 'Lightning-fast build tool and dev server' },
            { name: 'React Router', description: 'Client-side routing for single-page application' },
            { name: 'Lucide React', description: 'Beautiful, customizable SVG icons' },
            { name: 'CSS3', description: 'Modern styling with grid, flexbox, and animations' }
        ],
        backend: [
            { name: 'FastAPI', description: 'High-performance Python web framework' },
            { name: 'Uvicorn', description: 'ASGI server for production deployment' },
            { name: 'Pydantic', description: 'Data validation and serialization' },
            { name: 'Python 3.9+', description: 'Modern Python with type hints' }
        ],
        ai: [
            { name: 'Anthropic Claude', description: 'Advanced AI for patent analysis and insights' },
            { name: 'Groq', description: 'High-speed inference for real-time processing' },
            { name: 'Custom NLP', description: 'Specialized models for patent text analysis' }
        ],
        testing: [
            { name: 'Jest', description: 'JavaScript testing framework' },
            { name: 'React Testing Library', description: 'Component testing utilities' },
            { name: 'Playwright', description: 'End-to-end testing automation' },
            { name: 'PyTest', description: 'Python testing framework' }
        ]
    }

    const features = [
        {
            icon: Brain,
            title: 'AI-Powered Analysis',
            description: 'Advanced machine learning algorithms analyze patent documents, research papers, and market data to provide comprehensive technology assessments.'
        },
        {
            icon: Search,
            title: 'Patent Intelligence',
            description: 'Real-time patent search and monitoring with intelligent filtering, similarity detection, and competitive landscape analysis.'
        },
        {
            icon: BarChart3,
            title: 'Market Analytics',
            description: 'Data-driven insights into technology trends, market opportunities, and commercialization potential with interactive visualizations.'
        },
        {
            icon: Bell,
            title: 'Smart Alerts',
            description: 'Automated monitoring system that tracks new patents, research publications, and market developments in your areas of interest.'
        },
        {
            icon: FileText,
            title: 'Comprehensive Reports',
            description: 'Generate detailed technology transfer reports with executive summaries, risk assessments, and actionable recommendations.'
        },
        {
            icon: Target,
            title: 'Novelty Assessment',
            description: 'Compare your innovations against existing patents and research to identify unique aspects and potential IP opportunities.'
        }
    ]

    const workflow = [
        {
            step: 1,
            title: 'Data Ingestion',
            description: 'Upload research documents, patents, or technology descriptions'
        },
        {
            step: 2,
            title: 'AI Analysis',
            description: 'Advanced NLP models extract key concepts and technical features'
        },
        {
            step: 3,
            title: 'Patent Search',
            description: 'Intelligent search across global patent databases for prior art'
        },
        {
            step: 4,
            title: 'Market Research',
            description: 'Analyze market trends, competitors, and commercialization opportunities'
        },
        {
            step: 5,
            title: 'Report Generation',
            description: 'Compile comprehensive insights into actionable reports'
        }
    ]

    return (
        <div className="about-page">
            <div className="about-container">
                {/* Hero Section */}
                <section className="about-hero">
                    <div className="hero-content">
                        <h1>EUREKA INDEX</h1>
                        <p className="hero-subtitle">AI-Powered Technology Transfer Analysis Platform</p>
                        <p className="hero-description">
                            Accelerating innovation by bridging the gap between research and commercialization through
                            intelligent patent analysis, market insights, and technology assessment.
                        </p>
                    </div>
                    <div className="hero-stats">
                        <div className="stat-item">
                            <div className="stat-number">10M+</div>
                            <div className="stat-label">Patents Analyzed</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-number">500+</div>
                            <div className="stat-label">Research Institutions</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-number">95%</div>
                            <div className="stat-label">Accuracy Rate</div>
                        </div>
                    </div>
                </section>

                {/* What We Do */}
                <section className="about-section">
                    <h2>What Does EUREKA INDEX Do?</h2>
                    <div className="section-content">
                        <p className="section-intro">
                            EUREKA INDEX is a comprehensive technology transfer platform that helps researchers,
                            universities, and organizations evaluate the commercial potential of their innovations.
                            We use advanced AI to analyze patents, assess market opportunities, and provide
                            actionable insights for technology commercialization.
                        </p>

                        <div className="features-grid">
                            {features.map((feature, index) => (
                                <div key={index} className="feature-card">
                                    <div className="feature-icon">
                                        <feature.icon size={24} />
                                    </div>
                                    <div className="feature-content">
                                        <h3>{feature.title}</h3>
                                        <p>{feature.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* How It Works */}
                <section className="about-section">
                    <h2>How It Works</h2>
                    <div className="workflow-container">
                        <div className="workflow-steps">
                            {workflow.map((item, index) => (
                                <div key={index} className="workflow-step">
                                    <div className="step-number">{item.step}</div>
                                    <div className="step-content">
                                        <h3>{item.title}</h3>
                                        <p>{item.description}</p>
                                    </div>
                                    {index < workflow.length - 1 && <div className="step-connector" />}
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* Scoring Methodology */}
                <section className="about-section">
                    <h2>AI Scoring Methodology & Algorithms</h2>
                    <div className="scoring-content">
                        <div className="scoring-overview">
                            <p>
                                EUREKA INDEX uses sophisticated multi-dimensional scoring algorithms to evaluate technology
                                transfer potential. Our AI-powered system analyzes over 15 key metrics with weighted scoring
                                to provide comprehensive assessments.
                            </p>
                        </div>

                        <div className="scoring-categories">
                            <div className="scoring-category">
                                <h3>Market Potential Score (0-10)</h3>
                                <div className="scoring-details">
                                    <div className="score-component">
                                        <h4>Market Size Analysis</h4>
                                        <div className="component-details">
                                            <p><strong>TAM Calculation:</strong> Total Addressable Market based on 25+ industry domains</p>
                                            <ul>
                                                <li>Healthcare: $580B TAM (8.9% CAGR)</li>
                                                <li>Space Tech: $485B TAM (15% CAGR)</li>
                                                <li>AI/ML: $380B TAM (25% CAGR)</li>
                                                <li>Defense Tech: $520B TAM (8.5% CAGR)</li>
                                                <li>Quantum Computing: $65B TAM (28% CAGR)</li>
                                            </ul>
                                            <p><strong>Weight:</strong> 30% of Market Potential Score</p>
                                            <p><strong>Formula:</strong> min(TAM_billions / 100, 10) × CAGR_factor</p>
                                        </div>
                                    </div>

                                    <div className="score-component">
                                        <h4>Commercial Activity Assessment</h4>
                                        <div className="component-details">
                                            <p><strong>Keywords Analysis:</strong> Scans for commercial indicators</p>
                                            <ul>
                                                <li>Commercial terms: "product", "market", "industry", "deployment"</li>
                                                <li>Business terms: "revenue", "customer", "manufacturing"</li>
                                                <li>Investment terms: "funding", "venture", "commercialization"</li>
                                            </ul>
                                            <p><strong>Weight:</strong> 25% of Market Potential Score</p>
                                            <p><strong>Threshold:</strong> Score &gt; 0.6 indicates high commercial readiness</p>
                                        </div>
                                    </div>

                                    <div className="score-component">
                                        <h4>Innovation Momentum</h4>
                                        <div className="component-details">
                                            <p><strong>Publication Velocity:</strong> Recent vs. total publication ratio</p>
                                            <p><strong>Formula:</strong> recent_publications(2_years) / total_publications × 1.5</p>
                                            <p><strong>Weight:</strong> 20% of Market Potential Score</p>
                                            <p><strong>Threshold:</strong> &gt; 0.3 indicates active research momentum</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="scoring-category">
                                <h3>Technology Readiness Level (TRL 1-9)</h3>
                                <div className="scoring-details">
                                    <div className="score-component">
                                        <h4>TRL Estimation Algorithm</h4>
                                        <div className="component-details">
                                            <p><strong>Keyword-Based Classification:</strong></p>
                                            <ul>
                                                <li>TRL 1-2: "theoretical", "basic principles", "fundamental research"</li>
                                                <li>TRL 3-4: "proof of concept", "laboratory", "validation"</li>
                                                <li>TRL 5-6: "prototype", "demonstration", "pilot scale"</li>
                                                <li>TRL 7-8: "system integration", "operational", "commercial"</li>
                                                <li>TRL 9: "deployed", "market proven", "full scale"</li>
                                            </ul>
                                            <p><strong>Patent Volume Adjustment:</strong> +0.5 TRL per 10 patents</p>
                                            <p><strong>Time to Market:</strong> TRL 8-9 = 1-2 years, TRL 1-3 = 8+ years</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="scoring-category">
                                <h3>Competitive Landscape Analysis</h3>
                                <div className="scoring-details">
                                    <div className="score-component">
                                        <h4>Intensity Scoring (0-10)</h4>
                                        <div className="component-details">
                                            <p><strong>Competition Thresholds:</strong></p>
                                            <ul>
                                                <li>High Intensity (8.5): &gt;100 competing documents</li>
                                                <li>Medium-High (6.5): 50-100 competing documents</li>
                                                <li>Medium (5.0): 20-50 competing documents</li>
                                                <li>Low (3.0): &lt;20 competing documents</li>
                                            </ul>
                                            <p><strong>Patent Density:</strong> patents / (patents + publications)</p>
                                            <p><strong>Positioning Score:</strong> Based on differentiation keywords</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="scoring-category">
                                <h3>IP Strength Assessment</h3>
                                <div className="scoring-details">
                                    <div className="score-component">
                                        <h4>Multi-Factor IP Score (0-10)</h4>
                                        <div className="component-details">
                                            <p><strong>Citation Analysis:</strong></p>
                                            <ul>
                                                <li>Citation Score: min(avg_citations / 10, 5) - Max 5 points</li>
                                                <li>Recency Score: recent_patents_ratio × 3 - Max 3 points</li>
                                                <li>Volume Score: min(patent_count / 20, 2) - Max 2 points</li>
                                            </ul>
                                            <p><strong>Freedom to Operate (FTO) Risk:</strong></p>
                                            <ul>
                                                <li>High Risk: &gt;50 blocking patents</li>
                                                <li>Medium Risk: 20-50 blocking patents</li>
                                                <li>Low Risk: &lt;20 blocking patents</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="scoring-category">
                                <h3>Regulatory Risk Assessment</h3>
                                <div className="scoring-details">
                                    <div className="score-component">
                                        <h4>Domain-Based Risk Scoring (1-9)</h4>
                                        <div className="component-details">
                                            <p><strong>Risk Categories:</strong></p>
                                            <ul>
                                                <li>Very High (9): Medical/Pharmaceutical - 5-10 years approval</li>
                                                <li>High (7): Automotive/Financial/Aerospace - 2-5 years</li>
                                                <li>Medium-High (6): Food/CleanTech - 1-3 years</li>
                                                <li>Medium (5): Energy/Telecom - 1-2 years</li>
                                                <li>Low-Medium (3): Software/Consumer - 3-6 months</li>
                                            </ul>
                                            <p><strong>Compliance Requirements:</strong> FDA, FCC, EPA, Safety Standards</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="scoring-category">
                                <h3>Resource Requirements Analysis</h3>
                                <div className="scoring-details">
                                    <div className="score-component">
                                        <h4>Complexity-Based Resource Estimation</h4>
                                        <div className="component-details">
                                            <p><strong>Complexity Classification:</strong></p>
                                            <ul>
                                                <li>High Complexity: Quantum, Nanotech, Biotech, AI/ML</li>
                                                <li>Medium Complexity: Automation, Software, Systems</li>
                                                <li>Low Complexity: Methods, Processes, Tools</li>
                                            </ul>
                                            <p><strong>Funding Estimates:</strong></p>
                                            <ul>
                                                <li>High: €10M - €100M+ (50+ specialists, 5-10 years)</li>
                                                <li>Medium: €1M - €10M (10-50 experts, 2-5 years)</li>
                                                <li>Low: €100K - €1M (3-10 people, 6 months - 2 years)</li>
                                            </ul>
                                            <p><strong>TRL Adjustment:</strong> Resource needs × (TRL / 5) scaling factor</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="scoring-weights">
                            <h3>Overall Assessment Weights</h3>
                            <div className="weights-grid">
                                <div className="weight-item">
                                    <div className="weight-label">Market Potential</div>
                                    <div className="weight-bar">
                                        <div className="weight-fill" style={{ width: '35%' }}></div>
                                    </div>
                                    <div className="weight-value">35%</div>
                                </div>
                                <div className="weight-item">
                                    <div className="weight-label">Technology Readiness</div>
                                    <div className="weight-bar">
                                        <div className="weight-fill" style={{ width: '25%' }}></div>
                                    </div>
                                    <div className="weight-value">25%</div>
                                </div>
                                <div className="weight-item">
                                    <div className="weight-label">IP Strength</div>
                                    <div className="weight-bar">
                                        <div className="weight-fill" style={{ width: '20%' }}></div>
                                    </div>
                                    <div className="weight-value">20%</div>
                                </div>
                                <div className="weight-item">
                                    <div className="weight-label">Competitive Position</div>
                                    <div className="weight-bar">
                                        <div className="weight-fill" style={{ width: '15%' }}></div>
                                    </div>
                                    <div className="weight-value">15%</div>
                                </div>
                                <div className="weight-item">
                                    <div className="weight-label">Regulatory Risk</div>
                                    <div className="weight-bar">
                                        <div className="weight-fill" style={{ width: '5%' }}></div>
                                    </div>
                                    <div className="weight-value">5%</div>
                                </div>
                            </div>
                        </div>

                        <div className="scoring-thresholds">
                            <h3>Decision Thresholds & Recommendations</h3>
                            <div className="thresholds-grid">
                                <div className="threshold-item excellent">
                                    <div className="threshold-score">8.0 - 10.0</div>
                                    <div className="threshold-label">Excellent Potential</div>
                                    <div className="threshold-action">Strong investment recommendation, immediate patent filing</div>
                                </div>
                                <div className="threshold-item good">
                                    <div className="threshold-score">6.0 - 7.9</div>
                                    <div className="threshold-label">Good Potential</div>
                                    <div className="threshold-action">Consider patent protection, tech transfer support</div>
                                </div>
                                <div className="threshold-item moderate">
                                    <div className="threshold-score">4.0 - 5.9</div>
                                    <div className="threshold-label">Moderate Potential</div>
                                    <div className="threshold-action">Monitor development, strategic guidance</div>
                                </div>
                                <div className="threshold-item emerging">
                                    <div className="threshold-score">2.0 - 3.9</div>
                                    <div className="threshold-label">Emerging Opportunity</div>
                                    <div className="threshold-action">Early stage research, publication focus</div>
                                </div>
                                <div className="threshold-item fundamental">
                                    <div className="threshold-score">0.0 - 1.9</div>
                                    <div className="threshold-label">Fundamental Research</div>
                                    <div className="threshold-action">Knowledge building, scientific publication</div>
                                </div>
                            </div>
                        </div>

                        <div className="ai-models">
                            <h3>AI Models & Processing</h3>
                            <div className="ai-models-grid">
                                <div className="ai-model">
                                    <h4>Natural Language Processing</h4>
                                    <ul>
                                        <li>Anthropic Claude for semantic analysis</li>
                                        <li>Custom keyword extraction algorithms</li>
                                        <li>Domain classification with 25+ categories</li>
                                        <li>Sentiment analysis for commercial readiness</li>
                                    </ul>
                                </div>
                                <div className="ai-model">
                                    <h4>Patent Similarity Engine</h4>
                                    <ul>
                                        <li>Vector embeddings for semantic similarity</li>
                                        <li>Citation network analysis</li>
                                        <li>Cross-reference validation</li>
                                        <li>Real-time patent database queries</li>
                                    </ul>
                                </div>
                                <div className="ai-model">
                                    <h4>Market Intelligence</h4>
                                    <ul>
                                        <li>Dynamic market size calculations</li>
                                        <li>CAGR-based growth projections</li>
                                        <li>Competitive landscape mapping</li>
                                        <li>Investment trend analysis</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Tech Stack */}
                <section className="about-section">
                    <h2>Technology Stack</h2>
                    <div className="tech-stack-grid">
                        <div className="tech-category">
                            <div className="category-header">
                                <Code size={20} />
                                <h3>Frontend</h3>
                            </div>
                            <div className="tech-list">
                                {techStack.frontend.map((tech, index) => (
                                    <div key={index} className="tech-item">
                                        <div className="tech-name">{tech.name}</div>
                                        <div className="tech-description">{tech.description}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="tech-category">
                            <div className="category-header">
                                <Database size={20} />
                                <h3>Backend</h3>
                            </div>
                            <div className="tech-list">
                                {techStack.backend.map((tech, index) => (
                                    <div key={index} className="tech-item">
                                        <div className="tech-name">{tech.name}</div>
                                        <div className="tech-description">{tech.description}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="tech-category">
                            <div className="category-header">
                                <Brain size={20} />
                                <h3>AI & ML</h3>
                            </div>
                            <div className="tech-list">
                                {techStack.ai.map((tech, index) => (
                                    <div key={index} className="tech-item">
                                        <div className="tech-name">{tech.name}</div>
                                        <div className="tech-description">{tech.description}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="tech-category">
                            <div className="category-header">
                                <CheckCircle size={20} />
                                <h3>Testing</h3>
                            </div>
                            <div className="tech-list">
                                {techStack.testing.map((tech, index) => (
                                    <div key={index} className="tech-item">
                                        <div className="tech-name">{tech.name}</div>
                                        <div className="tech-description">{tech.description}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* Technical Architecture */}
                <section className="about-section">
                    <h2>Technical Architecture</h2>
                    <div className="architecture-content">
                        <div className="architecture-overview">
                            <p>
                                EUREKA INDEX is built on a modern, scalable architecture designed for high-performance
                                patent analysis and real-time insights delivery.
                            </p>
                        </div>

                        <div className="architecture-features">
                            <div className="arch-feature">
                                <Zap className="arch-icon" />
                                <div className="arch-content">
                                    <h4>High Performance</h4>
                                    <p>FastAPI backend with async processing and Vite frontend for lightning-fast user experience</p>
                                </div>
                            </div>

                            <div className="arch-feature">
                                <Shield className="arch-icon" />
                                <div className="arch-content">
                                    <h4>Secure & Reliable</h4>
                                    <p>Enterprise-grade security with data validation, type safety, and comprehensive testing</p>
                                </div>
                            </div>

                            <div className="arch-feature">
                                <Globe className="arch-icon" />
                                <div className="arch-content">
                                    <h4>Scalable Design</h4>
                                    <p>Microservices architecture with RESTful APIs and modular component structure</p>
                                </div>
                            </div>

                            <div className="arch-feature">
                                <Cpu className="arch-icon" />
                                <div className="arch-content">
                                    <h4>AI Integration</h4>
                                    <p>Seamless integration with multiple AI providers for robust natural language processing</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Use Cases */}
                <section className="about-section">
                    <h2>Who Uses EUREKA INDEX?</h2>
                    <div className="use-cases-grid">
                        <div className="use-case">
                            <Users className="use-case-icon" />
                            <h3>Research Institutions</h3>
                            <p>Universities and research centers evaluating the commercial potential of their innovations and identifying licensing opportunities.</p>
                        </div>

                        <div className="use-case">
                            <Lightbulb className="use-case-icon" />
                            <h3>Technology Transfer Offices</h3>
                            <p>TTOs streamlining their evaluation process and making data-driven decisions about patent portfolios and commercialization strategies.</p>
                        </div>

                        <div className="use-case">
                            <Rocket className="use-case-icon" />
                            <h3>Startups & Entrepreneurs</h3>
                            <p>Early-stage companies conducting freedom-to-operate analysis and identifying white space opportunities in competitive markets.</p>
                        </div>
                    </div>
                </section>

                {/* Interview Summary */}
                <section className="about-section interview-section">
                    <h2>Project Summary for Interviews</h2>
                    <div className="interview-content">
                        <div className="interview-card">
                            <h3>Project Overview</h3>
                            <p>
                                EUREKA INDEX is a full-stack web application that leverages artificial intelligence
                                to accelerate technology transfer by providing comprehensive patent analysis, market
                                insights, and commercialization assessments. The platform helps bridge the gap between
                                academic research and commercial applications.
                            </p>
                        </div>

                        <div className="interview-card">
                            <h3>Key Technical Achievements</h3>
                            <ul>
                                <li>Built responsive React frontend with modern hooks and routing</li>
                                <li>Developed FastAPI backend with async processing and type safety</li>
                                <li>Integrated multiple AI APIs for natural language processing</li>
                                <li>Implemented comprehensive testing suite (unit, integration, E2E)</li>
                                <li>Created scalable component architecture with reusable UI elements</li>
                                <li>Designed professional, accessible user interface</li>
                            </ul>
                        </div>

                        <div className="interview-card">
                            <h3>Problem Solved</h3>
                            <p>
                                Traditional technology transfer is slow and relies heavily on manual analysis.
                                EUREKA INDEX automates patent research, provides AI-powered insights, and delivers
                                actionable recommendations, reducing evaluation time from weeks to hours while
                                improving accuracy and comprehensiveness.
                            </p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    )
}

export default About
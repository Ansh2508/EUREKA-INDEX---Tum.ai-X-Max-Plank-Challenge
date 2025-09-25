#!/bin/bash

# Semantic Patent Alerts Setup Script
echo "🚀 Setting up Semantic Patent Alerts Application"

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download required models
echo "🤖 Downloading AI models..."
python -c "
from sentence_transformers import SentenceTransformer
print('Downloading sentence transformer model...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model downloaded successfully!')
"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p temp
mkdir -p data

# Set up environment variables
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOL
# API Keys
LOGIC_MILL_API_TOKEN=your_logic_mill_token_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here

# AWS Configuration (for Alexa integration)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# Database Configuration
DATABASE_URL=sqlite:///./patent_alerts.db

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
EOL
    echo "📝 Created .env file. Please update with your API keys."
else
    echo "✅ .env file already exists"
fi

# Initialize database (if using SQLAlchemy)
echo "🗄️ Initializing database..."
python -c "
print('Database initialization would go here')
# In production: run Alembic migrations
"

echo "✅ Setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Run: uvicorn main:app --reload"
echo "3. Open: http://localhost:8000/dashboard"
echo ""
echo "📚 Available endpoints:"
echo "- / : Basic analysis interface"
echo "- /dashboard : Enhanced dashboard"
echo "- /comprehensive-analysis : Full patent intelligence"
echo "- /semantic-alerts : Patent similarity alerts"
echo "- /competitor-discovery : Find key players"
echo "- /licensing-opportunities : Licensing mapping"
echo "- /novelty-assessment : Automated novelty analysis"
echo "- /voice-query : Voice interface (Alexa integration)" 
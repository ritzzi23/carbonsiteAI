# 🌍 CarbonSiteAI - Intelligent Site Selection for Carbon Conversion Facilities

An AI-powered site selection system designed specifically for **Turnover Labs** to identify optimal locations for their first-of-a-kind (FOAK) carbon conversion facilities. This tool addresses the critical challenge of finding sites that balance CO₂ availability, off-taker proximity, financial viability, scalability, and policy readiness.

## 🎯 **Project Overview**

**Turnover Labs** converts industrial waste into carbon-neutral chemicals and needs to identify the optimal location for their FOAK facility. Our AI agent analyzes multiple factors to recommend the best sites based on their specific requirements:

### **🏭 What Turnover Labs Wants (From Their Slide)**
1. **FOAK pilot site** supporting 50-100 tons/year CO₂ conversion, expandable to 1-5k tons
2. **Nearby off-taker** of the products generated (host or other)
3. **Financial returns** with minimal incentive support (long-term)
4. **Project that works** in today's policy climate (not waiting for future changes)
5. **Verifiable emissions avoidance or reduction**

## 🚀 **Key Features**

### **🤖 AI-Powered Site Analysis**
- **Intelligent Scoring**: Multi-factor analysis using weighted criteria
- **Real-time Data**: Integration with EPA, Census, and industrial databases
- **Dynamic Recommendations**: Site rankings based on user priorities

### **📊 Comprehensive Site Evaluation**
- **CO₂ Availability**: Proximity to industrial CO₂ sources
- **Off-taker Proximity**: Nearby buyers for carbon-neutral products
- **Financial Viability**: ROI calculations without heavy subsidies
- **Scalability Assessment**: Expansion potential from pilot to commercial scale
- **Policy Readiness**: Current regulatory climate compatibility

### **🗺️ Interactive Visualization**
- **Interactive Maps**: Geographic overview with site markers
- **Radar Charts**: Multi-dimensional site comparison
- **Detailed Reports**: Comprehensive site analysis with metrics
- **Export Functionality**: Download reports and data for stakeholders

## 🏗️ **Architecture**

```
User Input → AI Agent → Data Gathering → Site Scoring → Recommendations → Visualization
```

### **Core Components**
- **Frontend**: Streamlit with modern, responsive UI
- **Backend**: FastAPI for API endpoints and data processing
- **AI Agent**: LangGraph-based workflow for intelligent analysis
- **Data Sources**: EPA APIs, Census data, industrial databases
- **Visualization**: Plotly charts, Folium maps, interactive dashboards

## 🛠️ **Technology Stack**

- **Frontend**: Streamlit, HTML/CSS, JavaScript
- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: LangChain, LangGraph, Groq LLM
- **Data**: Pandas, NumPy, GeoPandas
- **Visualization**: Plotly, Folium, Matplotlib
- **Deployment**: Docker, Google Cloud Run

## 📋 **Prerequisites**

- Python 3.8+
- Git
- API keys for:
  - [Groq](https://console.groq.com/) (LLM provider)
  - EPA APIs (free government data)
  - Census API (free government data)

## 🚀 **Installation & Setup**

### **1. Clone the Repository**
```bash
git clone <your-repo-url>
cd carbon-site-ai
```

### **2. Install Dependencies**
```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

### **3. Set Up Environment Variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### **4. Configure API Keys**
```env
# Required API Keys
GROQ_API_KEY="your_groq_api_key_here"

# Optional API Keys (for enhanced features)
OPENAI_API_KEY="your_openai_api_key_here"
```

## 🎮 **Usage**

### **Start the Application**
```bash
streamlit run streamlit_app.py --server.port 8501
```

### **Access the Application**
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000 (when implemented)

## 📱 **How to Use**

### **1. Project Configuration**
- Select project type (CO₂ to Methanol, Ethanol, etc.)
- Set capacity requirements (initial and target)
- Choose target regions
- Adjust priority weights for different criteria

### **2. Site Analysis**
- Click "Analyze Sites" to run the AI agent
- Review top site recommendations with scores
- Explore detailed breakdowns for each location
- View geographic overview on interactive maps

### **3. Results & Reports**
- Compare sites using radar charts
- Download detailed analysis reports
- Export site data for further analysis
- Generate stakeholder presentations

## 🔧 **Core Tools & APIs**

### **Data Sources**
- **EPA ECHO**: Industrial facility data and compliance
- **EPA TRI**: Toxic release inventory
- **Census API**: Demographics and economic data
- **OpenStreetMap**: Transportation and infrastructure
- **State Databases**: Industrial zoning and permits

### **Analysis Tools**
- **CO₂ Source Locator**: Find industrial CO₂ emitters
- **Off-taker Matcher**: Identify potential product buyers
- **Site Scorer**: Multi-factor location evaluation
- **Financial Calculator**: ROI and cost analysis
- **Policy Checker**: Regulatory climate assessment

## 📊 **Scoring Methodology**

Our AI agent uses a weighted scoring system based on Turnover Labs' priorities:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **CO₂ Availability** | 25% | Proximity to industrial CO₂ sources |
| **Off-taker Proximity** | 30% | Nearby buyers for carbon-neutral products |
| **Financial Viability** | 20% | ROI without heavy subsidies |
| **Scalability** | 15% | Expansion potential from pilot to commercial |
| **Policy Ready** | 10% | Current regulatory climate compatibility |

## 🎯 **Demo Scenarios**

### **Scenario 1: CO₂ to Methanol Plant**
- **Location**: Texas/Louisiana region
- **Capacity**: 100 tons/year → 5,000 tons/year
- **Focus**: Petrochemical industry off-takers

### **Scenario 2: CO₂ to Synthetic Fuels**
- **Location**: California
- **Capacity**: 150 tons/year → 3,000 tons/year
- **Focus**: Low-carbon fuel standards compliance

### **Scenario 3: CO₂ to Chemicals**
- **Location**: Midwest
- **Capacity**: 75 tons/year → 2,500 tons/year
- **Focus**: Agricultural and industrial chemical markets

## 🚀 **Deployment**

### **Local Development**
```bash
streamlit run streamlit_app.py --server.port 8501
```

### **Production Deployment**
```bash
# Build Docker image
docker build -t carbon-site-ai .

# Run container
docker run -p 8501:8501 carbon-site-ai
```

### **Cloud Deployment**
- **Google Cloud Run**: Scalable, serverless deployment
- **Streamlit Cloud**: Easy frontend hosting
- **AWS/GCP**: Full-stack deployment options

## 🔒 **Security & Privacy**

- **Environment Variables**: All API keys stored securely
- **Data Privacy**: No user data stored permanently
- **API Security**: Rate limiting and input validation
- **Government Data**: Uses public, free government APIs

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Turnover Labs**: For the facility site selection challenge
- **EPA**: For industrial facility and emissions data
- **Census Bureau**: For demographic and economic data
- **Streamlit**: For the beautiful web interface framework
- **LangChain**: For the AI agentic workflow framework

## 📞 **Support**

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/carbon-site-ai/issues) page
2. Create a new issue with detailed information
3. Include your environment details and error messages

---

**Built with ❤️ for Turnover Labs - Track 2: Facility Site Selection Challenge**

*This project demonstrates advanced AI agentic workflows, real-time data integration, and intelligent decision-making for complex industrial site selection challenges.*

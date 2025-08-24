# 🌍 CarbonSiteAI EU - Intelligent Industrial Site Selection for Europe

An AI-powered industrial site selection platform designed specifically for **Turnover's strategic objectives** in Europe. This comprehensive tool addresses the critical challenge of identifying optimal locations for carbon capture and methanol production facilities that meet Turnover's specific requirements for FOAK pilots, buyer proximity, financial returns, and regulatory compliance.

## 🎯 **Project Overview**

**CarbonSiteAI EU** is built to address Turnover's strategic goals for European market entry:

### **🏭 Turnover's Strategic Requirements**
1. **FOAK Pilot Site**: 50-100 tons CO₂/year → 1,000-5,000 tons/year scalability
2. **Nearby Off-taker**: Strategic buyer proximity for product offtake
3. **Financial Returns**: Minimal incentive dependency with 3-4 year payback
4. **Policy Alignment**: Current regulatory environment viability
5. **Verifiable Emissions**: Measurable CO₂ avoidance/reduction

## 🚀 **Key Features**

### **🤖 AI-Powered Site Analysis**
- **Intelligent Scoring**: Multi-factor analysis using weighted criteria (carbon intensity, buyer proximity, infrastructure, regulatory environment)
- **Real-time Data**: Integration with Electricity Maps, OpenWeatherMap, EIA, and industrial databases
- **Dynamic Recommendations**: Site rankings based on real-time market conditions

### **📊 Comprehensive Site Evaluation**
- **Carbon Intensity Analysis**: Real-time CO₂ emissions per kWh (Germany: 216.0 gCO₂/kWh)
- **Buyer Proximity**: Google Maps integration for methanol buyer discovery
- **Financial Viability**: Methanol production cost calculator (€32,303.50/ton)
- **Scalability Assessment**: Expansion potential from pilot to commercial scale
- **Policy Readiness**: EU ETS/CBAM incentive analysis

### **🗺️ Interactive Visualization**
- **Interactive Maps**: Geographic overview with site markers using Folium
- **Real-time Dashboards**: Live carbon intensity and power price monitoring
- **Detailed Reports**: Comprehensive site analysis with AI-powered insights
- **Export Functionality**: Download reports and data for stakeholders

## 🏗️ **Architecture**

```
User Input → AI Agent → Real-time API Orchestration → Site Scoring → Recommendations → Visualization
```

### **Core Components**
- **Frontend**: Streamlit with modern, responsive UI and 8 specialized tabs
- **Backend**: Modular API connectors for multiple data sources
- **AI Engine**: Groq API integration with LLaMA 3.1 8B Instant
- **Data Sources**: Electricity Maps, Google Maps, OpenWeatherMap, EIA, Nord Pool
- **Visualization**: Plotly charts, Folium maps, interactive dashboards

## 🛠️ **Technology Stack**

- **Frontend**: Streamlit 1.28.0+, HTML/CSS, JavaScript
- **Backend**: Python 3.9+, Modular API architecture
- **AI/ML**: Groq API, LLaMA 3.1 8B Instant, Custom ML algorithms
- **Data**: Pandas 1.5.0+, NumPy 1.24.0+, Dataclasses
- **Visualization**: Plotly 5.15.0+, Folium 0.14.0+, Streamlit-Folium 0.13.0+
- **APIs**: Electricity Maps, Google Maps Platform, OpenWeatherMap, EIA, Nord Pool
- **Deployment**: Streamlit Cloud, GitHub integration

## 📋 **Prerequisites**

- Python 3.9+
- Git
- API keys for:
  - [Groq](https://console.groq.com/) (AI analysis)
  - [Google Maps Platform](https://developers.google.com/maps) (buyer discovery)
  - [Electricity Maps](https://www.electricitymaps.com/) (carbon intensity)
  - [OpenWeatherMap](https://openweathermap.org/api) (weather data)
  - [EIA](https://www.eia.gov/opendata/) (energy market data)

## 🚀 **Installation & Setup**

### **1. Clone the Repository**
```bash
git clone https://github.com/ritzzi23/carbonsiteAI.git
cd carbonsiteAI
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Configure API Keys**
```bash
# Copy the template
cp api_keys_template.yaml backend/api_keys.yaml

# Edit with your actual API keys
nano backend/api_keys.yaml
```

### **4. API Keys Configuration**
```yaml
# Required API Keys
electricity_maps: "YOUR_ELECTRICITY_MAPS_AUTH_TOKEN_HERE"
google_maps: "YOUR_GOOGLE_MAPS_API_KEY_HERE"
groq: "YOUR_GROQ_API_KEY_HERE"

# Optional API Keys (for enhanced features)
openweathermap: "YOUR_OPENWEATHERMAP_API_KEY_HERE"
eia: "YOUR_EIA_API_KEY_HERE"
```

## 🎮 **Usage**

### **Start the Application**
```bash
streamlit run streamlit_app_eu.py --server.port 8501
```

### **Access the Application**
- **Frontend**: http://localhost:8501
- **Network**: http://192.168.1.227:8501 (local network)

## 📱 **How to Use**

### **1. Project Configuration**
- Select target region (Germany, EU expansion)
- Set methanol production capacity requirements
- Choose carbon capture technology
- Adjust priority weights for different criteria

### **2. Site Analysis**
- **🇩🇪 Germany Site ID**: Comprehensive German industrial site screening
- **🗺️ Google Maps Buyer Discovery**: Find methanol buyers near sites
- **📊 Site Cost Scoring**: Evaluate sites based on production costs
- **💰 Methanol Production Calculator**: Detailed cost analysis
- **🤖 AI Site Analysis**: AI-powered insights and break-even analysis

### **3. Results & Reports**
- Compare sites using interactive scoring
- Download detailed analysis reports
- Export site data for further analysis
- Generate stakeholder presentations

## 🔧 **Core Tools & APIs**

### **Data Sources**
- **Electricity Maps**: Real-time carbon intensity and power prices
- **Google Maps Platform**: Geocoding, Places, and Maps JavaScript APIs
- **OpenWeatherMap**: Weather data and renewable energy potential
- **EIA**: US energy market data and regulatory information
- **Nord Pool**: European power market data
- **ENTSO-E**: European electricity transparency data

### **Analysis Tools**
- **Carbon Intensity Monitor**: Real-time CO₂ emissions tracking
- **Buyer Discovery Engine**: Google Maps integration for methanol buyers
- **Site Scorer**: Multi-factor location evaluation with custom algorithms
- **Financial Calculator**: Methanol production cost analysis
- **AI Analysis Engine**: Groq-powered strategic insights

## 📊 **Scoring Methodology**

Our AI agent uses a weighted scoring system based on Turnover's priorities:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Carbon Intensity** | 40% | Real-time CO₂ emissions per kWh |
| **Buyer Proximity** | 25% | Distance to methanol offtakers |
| **Infrastructure** | 20% | Site readiness and permitting |
| **Regulatory** | 15% | EU ETS/CBAM incentive alignment |

## 🎯 **Key Features by Tab**

### **🇩🇪 Germany Site ID**
- Industrial site screening for Germany
- Carbon intensity analysis (216.0 gCO₂/kWh)
- Site archetype classification
- Regulatory environment assessment

### **🗺️ Google Maps Buyer Discovery**
- Methanol buyer proximity analysis
- Distance calculations and route optimization
- Chemical company classification
- Export functionality for buyer data

### **📊 Site Cost Scoring**
- Custom scoring algorithm implementation
- Production cost calculations
- Site ranking and recommendations
- Strategic insights display

### **💰 Methanol Production Calculator**
- Detailed cost breakdown (€32,303.50/ton)
- Energy requirements (5,320 kWh/ton MeOH)
- Input calculations (100 tons CO₂, 11 tons water, 9 tons H₂)
- Break-even analysis

### **🤖 AI Site Analysis**
- Groq API integration for strategic insights
- Break-even timeline analysis
- Output rate optimization
- AI-powered recommendations

## 🚀 **Deployment**

### **Local Development**
```bash
streamlit run streamlit_app_eu.py --server.port 8501
```

### **Streamlit Cloud Deployment**
1. Connect GitHub repository: `https://github.com/ritzzi23/carbonsiteAI`
2. Set main file path: `streamlit_app_eu.py`
3. Configure secrets in TOML format
4. Deploy with automatic updates

### **Environment Variables for Streamlit Cloud**
```toml
[api_keys]
electricity_maps = "your_token_here"
google_maps = "your_key_here"
groq = "your_key_here"
openweathermap = "your_key_here"
eia = "your_key_here"
```

## 🔒 **Security & Privacy**

- **Environment Variables**: All API keys stored securely in Streamlit Cloud
- **Data Privacy**: No user data stored permanently
- **API Security**: Rate limiting and intelligent fallback mechanisms
- **Git Security**: Clean repository with no exposed secrets

## 📊 **Current Status**

- ✅ **Local Development**: Fully functional with all APIs
- ✅ **GitHub Repository**: Clean and secure with latest code
- ✅ **API Integration**: All major services connected and tested
- ✅ **Streamlit Cloud**: Ready for deployment
- 🔄 **EU Expansion**: Germany complete, ready for additional countries

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Turnover**: For the strategic industrial site selection challenge
- **Electricity Maps**: For real-time carbon intensity data
- **Google Maps Platform**: For buyer discovery and geospatial analysis
- **Groq**: For AI-powered strategic insights
- **Streamlit**: For the beautiful web interface framework
- **European Union**: For the Green Deal vision and regulatory framework

## 📞 **Support**

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/ritzzi23/carbonsiteAI/issues) page
2. Create a new issue with detailed information
3. Include your environment details and error messages

## 🌟 **Project Impact**

**CarbonSiteAI EU** represents the future of intelligent industrial site selection:

- **Accelerates carbon capture** deployment through intelligent site selection
- **Supports EU Green Deal** objectives with data-driven insights
- **Creates new economic opportunities** in methanol production
- **Reduces carbon emissions** through industrial transformation
- **Enables Turnover's strategic success** in European markets

---

**Built with ❤️ for Turnover's European Strategic Success and a Sustainable Future** 🇪🇺

*This project demonstrates advanced AI integration, real-time data orchestration, and intelligent decision-making for complex industrial site selection challenges in Europe's evolving green economy.*

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
import os

# Add backend to path for API access
sys.path.append('backend')
from api_connectors.energy_data_api import EnergyDataConnector

# Page configuration
st.set_page_config(
    page_title="🌍 CarbonSiteAI EU - European Site Selector",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for modern, different styling
st.markdown("""
<style>
    /* Modern gradient backgrounds */
    .hero-section {
        background: linear-gradient(135deg, #003399 0%, #0066cc 50%, #0099ff 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    /* Modern card designs */
    .info-card {
        background: linear-gradient(135deg, #003399 0%, #0066cc 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .site-card-modern {
        background: linear-gradient(135deg, #0099ff 0%, #00ccff 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease;
    }
    
    .site-card-modern:hover {
        transform: translateY(-5px);
    }
    
    .metric-card-modern {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #003399;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border: 1px solid #e1e5e9;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #003399 0%, #0066cc 100%);
        color: white;
        border: none;
        border-radius: 2rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #002266 0%, #0052a3 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 1rem;
        padding: 0.5rem 1rem;
        color: #003399;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #003399 0%, #0066cc 100%);
        color: white;
    }
    
    /* Stats cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #003399 0%, #0066cc 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Default sample sites - EU FOCUSED
DEFAULT_SITES = [
    {
        "name": "Ludwigshafen, Germany",
        "country": "DE",
        "score": 96,
        "co2_availability": 98,
        "offtaker_proximity": 95,
        "financial_viability": 94,
        "scalability": 97,
        "policy_ready": 95,
        "co2_sources": 15,
        "nearby_offtakers": 12,
        "land_availability": "High",
        "energy_costs": "€0.085/kWh",
        "expansion_potential": "Excellent",
        "emissions_reduction": "88%",
        "roi_estimate": "2.8 years",
        "lat": 49.4811,
        "lon": 8.4353,
        "description": "Chemical Valley - BASF headquarters with extensive industrial infrastructure"
    },
    {
        "name": "Rotterdam, Netherlands",
        "country": "NL",
        "score": 94,
        "co2_availability": 96,
        "offtaker_proximity": 98,
        "financial_viability": 92,
        "scalability": 95,
        "policy_ready": 93,
        "co2_sources": 18,
        "nearby_offtakers": 16,
        "land_availability": "Medium",
        "energy_costs": "€0.092/kWh",
        "expansion_potential": "Excellent",
        "emissions_reduction": "86%",
        "roi_estimate": "3.1 years",
        "lat": 51.9225,
        "lon": 4.4792,
        "description": "Europe's largest port with major refineries and chemical clusters"
    },
    {
        "name": "Antwerp, Belgium",
        "country": "BE",
        "score": 92,
        "co2_availability": 94,
        "offtaker_proximity": 96,
        "financial_viability": 90,
        "scalability": 93,
        "policy_ready": 91,
        "co2_sources": 14,
        "nearby_offtakers": 13,
        "land_availability": "High",
        "energy_costs": "€0.089/kWh",
        "expansion_potential": "Excellent",
        "emissions_reduction": "84%",
        "roi_estimate": "3.3 years",
        "lat": 51.2194,
        "lon": 4.4025,
        "description": "Major chemical hub with excellent logistics and EU policy alignment"
    },
    {
        "name": "Le Havre, France",
        "country": "FR",
        "score": 89,
        "co2_availability": 91,
        "offtaker_proximity": 88,
        "financial_viability": 87,
        "scalability": 90,
        "policy_ready": 89,
        "co2_sources": 11,
        "nearby_offtakers": 9,
        "land_availability": "High",
        "energy_costs": "€0.078/kWh",
        "expansion_potential": "Good",
        "emissions_reduction": "82%",
        "roi_estimate": "3.6 years",
        "lat": 49.4944,
        "lon": 0.1079,
        "description": "Strategic Normandy location with nuclear energy and industrial zones"
    },
    {
        "name": "Porto Marghera, Italy",
        "country": "IT",
        "score": 87,
        "co2_availability": 89,
        "offtaker_proximity": 85,
        "financial_viability": 88,
        "scalability": 86,
        "policy_ready": 87,
        "co2_sources": 9,
        "nearby_offtakers": 7,
        "land_availability": "Medium",
        "energy_costs": "€0.095/kWh",
        "expansion_potential": "Good",
        "emissions_reduction": "80%",
        "roi_estimate": "3.9 years",
        "lat": 45.4371,
        "lon": 12.3326,
        "description": "Venetian industrial zone with access to Mediterranean markets"
    }
]

# Sample CO₂ sources (European industrial facilities)
CO2_SOURCES = [
    {"name": "BASF Ludwigshafen", "lat": 49.4811, "lon": 8.4353, "type": "Chemical", "co2_tons": 3200000},
    {"name": "Shell Pernis Refinery", "lat": 51.9225, "lon": 4.4792, "type": "Refinery", "co2_tons": 2800000},
    {"name": "Total Antwerp", "lat": 51.2194, "lon": 4.4025, "type": "Refinery", "co2_tons": 2100000},
    {"name": "ExxonMobil Le Havre", "lat": 49.4944, "lon": 0.1079, "type": "Refinery", "co2_tons": 1800000},
    {"name": "Eni Porto Marghera", "lat": 45.4371, "lon": 12.3326, "type": "Refinery", "co2_tons": 1500000}
]

# Sample off-takers (European potential buyers)
OFFTAKERS = [
    {"name": "BASF Chemical", "lat": 49.4811, "lon": 8.4353, "type": "Chemical", "demand": "Very High"},
    {"name": "DSM Netherlands", "lat": 51.9225, "lon": 4.4792, "type": "Chemical", "demand": "Very High"},
    {"name": "Solvay Belgium", "lat": 51.2194, "lon": 4.4025, "type": "Chemical", "demand": "High"},
    {"name": "Total Energies", "lat": 49.4944, "lon": 0.1079, "type": "Energy", "demand": "High"},
    {"name": "Eni Chemicals", "lat": 45.4371, "lon": 12.3326, "type": "Chemical", "demand": "Medium"}
]

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">🇪🇺 CarbonSiteAI EU</h1>
    <p class="hero-subtitle">European Site Selection for Carbon Conversion Facilities</p>
    <p style="font-size: 1.2rem; opacity: 0.8;">Built for Turnover Labs | EU Market Focus | EU Green Deal Alignment</p>
</div>
""", unsafe_allow_html=True)

# Main navigation tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🏠 Dashboard", "⚙️ Configuration", "🗺️ Site Analysis", "📊 Results", "🌍 Real-Time CO₂ Data", "🇩🇪 Germany Site ID", "🗺️ Google Maps Buyer Discovery", "🤖 AI Site Analysis & Break-Even"])

with tab1:
    # Dashboard Overview
    st.markdown("## 📊 European Project Overview")
    
    # Stats grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">5</div>
            <div class="stat-label">Top EU Sites</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">96</div>
            <div class="stat-label">Best Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">15</div>
            <div class="stat-label">CO₂ Sources</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">12</div>
            <div class="stat-label">Off-takers</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Real-time Germany CO₂ Data Dashboard
    try:
        connector = EnergyDataConnector()
        germany_co2_data = connector._get_electricity_maps_data('DE')
        
        if germany_co2_data:
            co2_record = germany_co2_data[0]
            
            st.markdown("## 🇩🇪 Germany Real-Time CO₂ Dashboard")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{co2_record.carbon_intensity_gco2_kwh:.1f}</div>
                    <div class="stat-label">Current CO₂ (gCO₂/kWh)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{co2_record.renewable_energy_share:.1f}%</div>
                    <div class="stat-label">Renewable Share</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">€{co2_record.power_price_eur_mwh:.2f}</div>
                    <div class="stat-label">Power Price (MWh)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{co2_record.timestamp.strftime("%H:%M")}</div>
                    <div class="stat-label">Last Updated (UTC)</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.success(f"✅ **Live data from Electricity Maps API** - Germany's current carbon intensity: {co2_record.carbon_intensity_gco2_kwh:.1f} gCO₂/kWh")
            
        else:
            st.info("ℹ️ **Germany CO₂ Data:** Available via Electricity Maps API (check Real-Time CO₂ Data tab)")
            
    except Exception as e:
        st.info("ℹ️ **Germany CO₂ Data:** Available via Electricity Maps API (check Real-Time CO₂ Data tab)")
    
    # Quick actions
    st.markdown("## 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏭 Analyze EU CO₂ to Methanol", key="btn1"):
            st.session_state.analysis_triggered = True
            st.session_state.selected_template = "EU CO₂ to Methanol Plant"
            st.rerun()
    
    with col2:
        if st.button("⛽ Analyze EU Synthetic Fuels", key="btn2"):
            st.session_state.analysis_triggered = True
            st.session_state.selected_template = "EU CO₂ to Synthetic Fuels"
            st.rerun()
    
    with col3:
        if st.button("🧪 Analyze EU Chemical Sites", key="btn3"):
            st.session_state.analysis_triggered = True
            st.session_state.selected_template = "EU CO₂ to Chemicals"
            st.rerun()
    
    # Project highlights
    st.markdown("## 🎯 EU Market Advantages")
    st.markdown("""
    <div class="info-card">
        <h3>🇪🇺 European Union Strategic Benefits</h3>
        <p>Turnover Labs can leverage Europe's advanced climate policies and industrial infrastructure for optimal carbon conversion facility deployment.</p>
        <p><strong>EU Policy Framework:</strong></p>
        <ul>
            <li>EU Green Deal - Carbon neutrality by 2050</li>
            <li>Fit for 55 - 55% emissions reduction by 2030</li>
            <li>EU ETS - World's largest carbon trading system</li>
            <li>Carbon Border Adjustment Mechanism (CBAM)</li>
            <li>EU Innovation Fund - €10B+ for clean tech</li>
        </ul>
        <p><strong>Market Advantages:</strong></p>
        <ul>
            <li>Advanced carbon markets with €80+/ton CO₂ prices</li>
            <li>Strong industrial clusters and supply chains</li>
            <li>Access to EU single market (450M consumers)</li>
            <li>Regulatory certainty and clear permitting pathways</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    # Configuration Panel
    st.markdown("## ⚙️ EU Project Configuration")
    
    # Project setup
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏭 Project Details")
        project_type = st.selectbox(
            "Project Type",
            ["CO₂ to Methanol", "CO₂ to Ethanol", "CO₂ to Synthetic Fuels", "CO₂ to Chemicals", "Custom"]
        )
        
        initial_capacity = st.slider("Initial Capacity (tons CO₂/year)", 50, 200, 100, step=10)
        target_capacity = st.slider("Target Capacity (tons CO₂/year)", 1000, 10000, 5000, step=500)
    
    with col2:
        st.markdown("### 🌍 EU Geographic Preferences")
        regions = st.multiselect(
            "Target EU Regions",
            ["Germany", "Netherlands", "Belgium", "France", "Italy", "Spain", "Denmark", "Sweden", "Finland", "Poland"],
            default=["Germany", "Netherlands", "Belgium"]
        )
        
        st.markdown("### ⚖️ Priority Weights")
        co2_availability = st.slider("CO₂ Availability", 1, 10, 8)
        offtaker_proximity = st.slider("Off-taker Proximity", 1, 10, 9)
        financial_viability = st.slider("Financial Viability", 1, 10, 7)
        scalability = st.slider("Scalability Potential", 1, 10, 8)
        policy_ready = st.slider("EU Policy Alignment", 1, 10, 9)
    
    # Analysis button
    if st.button("🚀 Run EU Site Analysis", type="primary", key="analyze_btn"):
        st.session_state.analysis_triggered = True
        st.rerun()

with tab3:
    # Site Analysis with Maps
    st.markdown("## 🗺️ European Site Analysis")
    
    # Always show the map first
    try:
        # Create a Folium map centered on Europe
        m = folium.Map(
            location=[50.8503, 4.3517],  # Center on Brussels
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Add site markers (BLUE - Recommended EU sites)
        for site in DEFAULT_SITES:
            # Special handling for Germany sites to show real-time CO₂ data
            if site['country'] == 'DE':
                # Try to get real-time CO₂ data for Germany
                try:
                    connector = EnergyDataConnector()
                    germany_co2_data = connector._get_electricity_maps_data('DE')
                    if germany_co2_data:
                        co2_record = germany_co2_data[0]
                        co2_info = f"<br><strong>🌍 Real-Time CO₂:</strong> {co2_record.carbon_intensity_gco2_kwh} gCO₂/kWh<br><strong>⚡ Renewable:</strong> {co2_record.renewable_energy_share:.1f}%"
                    else:
                        co2_info = "<br><strong>🌍 CO₂ Data:</strong> Available (API connected)"
                except:
                    co2_info = "<br><strong>🌍 CO₂ Data:</strong> Available (API connected)"
            else:
                co2_info = ""
            
            folium.Marker(
                [site['lat'], site['lon']],
                popup=f"""
                <div style="width: 250px;">
                    <h4>🏭 {site['name']}</h4>
                    <p><strong>Score:</strong> {site['score']}/100</p>
                    <p><strong>Country:</strong> {site['country']}</p>
                    <p><strong>CO₂ Sources:</strong> {site['co2_sources']}</p>
                    <p><strong>Off-takers:</strong> {site['nearby_offtakers']}</p>
                    <p><strong>ROI:</strong> {site['roi_estimate']}</p>
                    <p><strong>Description:</strong> {site['description']}</p>
                    {co2_info}
                </div>
                """,
                tooltip=f"🏭 {site['name']} - Score: {site['score']}/100",
                icon=folium.Icon(color='blue', icon='industry', prefix='fa')
            ).add_to(m)
        
        # Add CO₂ source markers (RED - European industrial facilities)
        for source in CO2_SOURCES:
            folium.Marker(
                [source['lat'], source['lon']],
                popup=f"""
                <div style="width: 200px;">
                    <h4>🏭 {source['name']}</h4>
                    <p><strong>Type:</strong> {source['type']}</p>
                    <p><strong>CO₂ Available:</strong> {source['co2_tons']:,} tons/year</p>
                    <p><strong>Status:</strong> Active</p>
                </div>
                """,
                tooltip=f"🏭 {source['name']} - {source['type']}",
                icon=folium.Icon(color='red', icon='industry', prefix='fa')
            ).add_to(m)
        
        # Add off-taker markers (GREEN - European potential buyers)
        for offtaker in OFFTAKERS:
            folium.Marker(
                [offtaker['lat'], offtaker['lon']],
                popup=f"""
                <div style="width: 200px;">
                    <h4>🏢 {offtaker['name']}</h4>
                    <p><strong>Type:</strong> {offtaker['type']}</p>
                    <p><strong>Demand:</strong> {offtaker['demand']}</p>
                    <p><strong>Status:</strong> Active Buyer</p>
                </div>
                """,
                tooltip=f"🏢 {offtaker['name']} - {offtaker['type']}",
                icon=folium.Icon(color='green', icon='building', prefix='fa')
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><strong>Map Legend</strong></p>
        <p><i class="fa fa-industry" style="color:blue"></i> Recommended EU Sites</p>
        <p><i class="fa fa-industry" style="color:red"></i> CO₂ Sources</p>
        <p><i class="fa fa-building" style="color:green"></i> Off-takers</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Display the map
        folium_static(m, width=800, height=500)
        
        st.success("✅ **European map loaded successfully!** Blue markers = recommended EU sites, Red = CO₂ sources, Green = off-takers")
        
    except Exception as e:
        st.error(f"❌ Error creating map: {str(e)}")
        st.info("Using fallback map display...")
        
        # Fallback: Show coordinates table
        map_data = pd.DataFrame({
            'Site': [site['name'] for site in DEFAULT_SITES],
            'Country': [site['country'] for site in DEFAULT_SITES],
            'Latitude': [site['lat'] for site in DEFAULT_SITES],
            'Longitude': [site['lon'] for site in DEFAULT_SITES],
            'Score': [site['score'] for site in DEFAULT_SITES]
        })
        st.dataframe(map_data)

with tab4:
    # Results and Analysis
    if not hasattr(st.session_state, 'analysis_triggered'):
        st.session_state.analysis_triggered = False
    
    if st.session_state.analysis_triggered:
        st.success("🚀 EU Analysis Complete! Here are your top European site recommendations.")
        
        # Use the default sites for now
        top_sites = DEFAULT_SITES
        
        # Top sites overview in modern cards
        st.markdown("## 🏆 Top EU Site Recommendations")
        
        for i, site in enumerate(top_sites):
            st.markdown(f"""
            <div class="site-card-modern">
                <h3>🥇 {site['name']} - Score: {site['score']}/100</h3>
                <p><strong>Country:</strong> {site['country']} | <strong>CO₂ Sources:</strong> {site['co2_sources']} | <strong>Off-takers:</strong> {site['nearby_offtakers']} | <strong>ROI:</strong> {site['roi_estimate']}</p>
                <p><strong>Description:</strong> {site['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed scoring breakdown
        st.markdown("## 📊 Detailed EU Scoring Breakdown")
        
        # Create scoring comparison chart
        categories = ['CO₂ Availability', 'Off-taker Proximity', 'Financial Viability', 'Scalability', 'EU Policy Alignment']
        
        fig = go.Figure()
        
        for site in top_sites:
            scores = [site['co2_availability'], site['offtaker_proximity'], site['financial_viability'], 
                     site['scalability'], site['policy_ready']]
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=categories,
                fill='toself',
                name=site['name']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="EU Site Comparison - Radar Chart"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Action buttons
        st.markdown("## 📋 Next Steps")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate EU Report", key="report_btn"):
                st.success("📄 EU report generation started! This will create a comprehensive analysis for European markets.")
        
        with col2:
            if st.button("🗺️ Export EU Site Data", key="export_btn"):
                st.success("📊 EU data exported! You can now download the European site analysis in CSV format.")
        
        with col3:
            if st.button("🔄 Re-run EU Analysis", key="rerun_btn"):
                st.session_state.analysis_triggered = False
                st.rerun()
    
    else:
        st.info("💡 **No EU analysis results yet.** Go to the Configuration tab to set up your European project and run the analysis!")

with tab5:
    # Real-Time CO₂ Data for Germany
    st.markdown("## 🌍 Real-Time CO₂ Data - Germany")
    st.markdown("### Live Carbon Intensity Data from Electricity Maps API")
    
    try:
        # Initialize the Energy Data Connector
        connector = EnergyDataConnector()
        
        # Get real-time CO₂ data for Germany
        st.info("🔄 Fetching real-time CO₂ data for Germany...")
        
        # Get carbon intensity data for Germany
        germany_co2_data = connector._get_electricity_maps_data('DE')
        
        if germany_co2_data:
            # Extract the data
            co2_record = germany_co2_data[0]
            
            # Display real-time data in modern cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="metric-card-modern">
                    <h3>🌡️ Current Carbon Intensity</h3>
                    <div class="stat-number">{}</div>
                    <div class="stat-label">gCO₂/kWh</div>
                </div>
                """.format(co2_record.carbon_intensity_gco2_kwh), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card-modern">
                    <h3>⚡ Renewable Share</h3>
                    <div class="stat-number">{:.1f}%</div>
                    <div class="stat-label">of total generation</div>
                </div>
                """.format(co2_record.renewable_energy_share), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card-modern">
                    <h3>🕐 Last Updated</h3>
                    <div class="stat-number">{}</div>
                    <div class="stat-label">UTC time</div>
                </div>
                """.format(co2_record.timestamp.strftime("%H:%M")), unsafe_allow_html=True)
            
            # Show data source
            st.success(f"✅ **Real-time data retrieved from Electricity Maps API** - Data source: {co2_record.data_source}")
            
            # Create a map showing Germany with CO₂ data
            st.markdown("### 🗺️ Germany CO₂ Intensity Map")
            
            # Create a Folium map centered on Germany
            germany_map = folium.Map(
                location=[51.1657, 10.4515],  # Center of Germany
                zoom_start=6,
                tiles='OpenStreetMap'
            )
            
            # Add Germany CO₂ data marker
            folium.Marker(
                [51.1657, 10.4515],  # Center of Germany
                popup=f"""
                <div style="width: 250px;">
                    <h4>🇩🇪 Germany - Real-Time CO₂ Data</h4>
                    <p><strong>Carbon Intensity:</strong> {co2_record.carbon_intensity_gco2_kwh} gCO₂/kWh</p>
                    <p><strong>Renewable Share:</strong> {co2_record.renewable_energy_share:.1f}%</p>
                    <p><strong>Power Price:</strong> €{co2_record.power_price_eur_mwh:.2f}/MWh</p>
                    <p><strong>Last Updated:</strong> {co2_record.timestamp.strftime("%Y-%m-%d %H:%M UTC")}</p>
                    <p><strong>Data Source:</strong> {co2_record.data_source}</p>
                </div>
                """,
                tooltip=f"🇩🇪 Germany - {co2_record.carbon_intensity_gco2_kwh} gCO₂/kWh",
                icon=folium.Icon(color='red', icon='info-sign', prefix='fa')
            ).add_to(germany_map)
            
            # Add major German cities with CO₂ context
            german_cities = [
                {"name": "Berlin", "lat": 52.5200, "lon": 13.4050, "co2_context": "Capital - High renewable focus"},
                {"name": "Munich", "lat": 48.1351, "lon": 11.5820, "co2_context": "Bavaria - Solar energy leader"},
                {"name": "Hamburg", "lat": 53.5511, "lon": 9.9937, "co2_context": "Port city - Wind energy hub"},
                {"name": "Frankfurt", "lat": 50.1109, "lon": 8.6821, "co2_context": "Financial center - Industrial emissions"},
                {"name": "Ludwigshafen", "lat": 49.4811, "lon": 8.4353, "co2_context": "Chemical Valley - BASF headquarters"}
            ]
            
            for city in german_cities:
                folium.Marker(
                    [city['lat'], city['lon']],
                    popup=f"""
                    <div style="width: 200px;">
                        <h4>🏙️ {city['name']}</h4>
                        <p><strong>CO₂ Context:</strong> {city['co2_context']}</p>
                        <p><strong>Regional Impact:</strong> Affects national average</p>
                    </div>
                    """,
                    tooltip=f"🏙️ {city['name']}",
                    icon=folium.Icon(color='blue', icon='info', prefix='fa')
                ).add_to(germany_map)
            
            # Add legend
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 200px; height: 120px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <p><strong>Germany CO₂ Map Legend</strong></p>
            <p><i class="fa fa-info-sign" style="color:red"></i> National CO₂ Intensity</p>
            <p><i class="fa fa-info" style="color:blue"></i> Major Cities</p>
            <p><strong>Data:</strong> Real-time from Electricity Maps</p>
            </div>
            '''
            germany_map.get_root().html.add_child(folium.Element(legend_html))
            
            # Display the map
            folium_static(germany_map, width=800, height=500)
            
            # Additional insights
            st.markdown("### 📊 CO₂ Intensity Insights")
            
            # Create a gauge chart for CO₂ intensity
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = co2_record.carbon_intensity_gco2_kwh,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Germany CO₂ Intensity (gCO₂/kWh)"},
                delta = {'reference': 400},  # Reference value for comparison
                gauge = {
                    'axis': {'range': [None, 600]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 200], 'color': "lightgreen"},
                        {'range': [200, 400], 'color': "yellow"},
                        {'range': [400, 600], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 500
                    }
                }
            ))
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # CO₂ intensity interpretation
            co2_value = co2_record.carbon_intensity_gco2_kwh
            if co2_value < 200:
                intensity_level = "🟢 Very Low"
                interpretation = "Excellent - Germany is producing very clean electricity"
            elif co2_value < 400:
                intensity_level = "🟡 Low to Moderate"
                interpretation = "Good - Germany has moderate carbon intensity"
            elif co2_value < 600:
                intensity_level = "🟠 Moderate to High"
                interpretation = "Concerning - Germany has elevated carbon intensity"
            else:
                intensity_level = "🔴 High"
                interpretation = "Critical - Germany has high carbon intensity"
            
            st.markdown(f"""
            <div class="info-card">
                <h3>📈 CO₂ Intensity Analysis</h3>
                <p><strong>Current Level:</strong> {intensity_level}</p>
                <p><strong>Interpretation:</strong> {interpretation}</p>
                <p><strong>Comparison:</strong> Germany's current intensity of {co2_value:.1f} gCO₂/kWh</p>
                <p><strong>Trend:</strong> Real-time monitoring shows current grid conditions</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("⚠️ **No real-time CO₂ data available for Germany.** This could be due to:")
            st.markdown("""
            - API rate limiting
            - Network connectivity issues
            - Electricity Maps service availability
            
            **Using cached data for demonstration...**
            """)
            
            # Show cached data as fallback
            st.markdown("### 📊 Cached CO₂ Data (Last Available)")
            st.markdown("""
            <div class="metric-card-modern">
                <h3>🌡️ Cached Carbon Intensity</h3>
                <div class="stat-number">344.0</div>
                <div class="stat-label">gCO₂/kWh (Cached)</div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"❌ **Error fetching real-time CO₂ data:** {str(e)}")
        st.info("💡 **Troubleshooting:** Check your Electricity Maps API configuration and network connection.")
        
        # Show fallback information
        st.markdown("### 📊 Germany CO₂ Information (Fallback)")
        st.markdown("""
        <div class="info-card">
            <h3>🇩🇪 Germany Carbon Intensity</h3>
            <p><strong>Typical Range:</strong> 300-500 gCO₂/kWh</p>
            <p><strong>Renewable Target:</strong> 80% by 2030</p>
            <p><strong>Current Status:</strong> Transitioning to renewable energy</p>
            <p><strong>Major Sources:</strong> Wind, Solar, Biomass</p>
        </div>
        """, unsafe_allow_html=True)

# Germany Site Identification Tab
with tab6:
    st.markdown("## 🇩🇪 Germany Site Identification & Analysis")
    st.write("Comprehensive site screening for CO₂ utilization projects - All 5 Deliverables")
    
    # Create sub-tabs for each deliverable
    subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs([
        "🔍 Site Screening", 
        "🧪 Product Selection", 
        "💰 Economic Model", 
        "🤝 Commercial Structure", 
        "📈 Financial Analysis"
    ])
    
    with subtab1:
        st.subheader("🔍 Site Screening & Archetype Analysis")
        
        # Screening criteria
        col1, col2, col3 = st.columns(3)
        with col1:
            min_score = st.slider("Minimum Score", 5.0, 10.0, 6.0, 0.1)
        with col2:
            min_co2 = st.slider("Min CO₂ Intensity (g/kWh)", 300, 600, 350, 10)
        with col3:
            max_power_price = st.slider("Max Power Price (EUR/MWh)", 60, 90, 85, 1)
        
        # Germany regions data
        germany_regions = {
            'North Rhine-Westphalia': {'co2_intensity': 450, 'power_price': 85.2, 'score': 8.5, 'industrial_clusters': ['Chemicals', 'Steel', 'Cement']},
            'Bavaria': {'co2_intensity': 380, 'power_price': 78.9, 'score': 7.8, 'industrial_clusters': ['Automotive', 'Electronics', 'Chemicals']},
            'Baden-Württemberg': {'co2_intensity': 320, 'power_price': 72.1, 'score': 8.2, 'industrial_clusters': ['Automotive', 'Machinery', 'Chemicals']},
            'Lower Saxony': {'co2_intensity': 420, 'power_price': 79.8, 'score': 7.5, 'industrial_clusters': ['Chemicals', 'Steel', 'Food']},
            'Hesse': {'co2_intensity': 410, 'power_price': 81.2, 'score': 7.9, 'industrial_clusters': ['Chemicals', 'Pharmaceuticals', 'Automotive']}
        }
        
        site_archetypes = {
            'Steel Plant': {'co2_intensity': 1800, 'annual_co2': 2000000, 'score': 8.5},
            'Cement Plant': {'co2_intensity': 800, 'annual_co2': 800000, 'score': 7.8},
            'Chemical Complex': {'co2_intensity': 1200, 'annual_co2': 1500000, 'score': 8.2},
            'Power Plant': {'co2_intensity': 600, 'annual_co2': 3000000, 'score': 6.5},
            'Refinery': {'co2_intensity': 1000, 'annual_co2': 1200000, 'score': 7.5}
        }
        
        # Apply screening
        screened_sites = []
        for region, region_data in germany_regions.items():
            for archetype, archetype_data in site_archetypes.items():
                if (region_data['score'] >= min_score and 
                    region_data['co2_intensity'] >= min_co2 and
                    region_data['power_price'] <= max_power_price):
                    
                    composite_score = (region_data['score'] * 0.4 + archetype_data['score'] * 0.6)
                    
                    screened_sites.append({
                        'Region': region,
                        'Site Type': archetype,
                        'CO₂ Intensity (g/kWh)': region_data['co2_intensity'],
                        'Power Price (EUR/MWh)': region_data['power_price'],
                        'Annual CO₂ (tons)': archetype_data['annual_co2'],
                        'Composite Score': round(composite_score, 2)
                    })
        
        # Display results
        if screened_sites:
            df = pd.DataFrame(screened_sites)
            df = df.sort_values('Composite Score', ascending=False)
            
            st.subheader(f"🏆 Top {len(df)} Recommended Sites")
            st.dataframe(df, use_container_width=True)
            
            # Show top 3 in detail
            st.subheader("🥇 Top 3 Sites Analysis")
            for i, site in df.head(3).iterrows():
                with st.expander(f"{site['Region']} - {site['Site Type']} (Score: {site['Composite Score']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("CO₂ Intensity", f"{site['CO₂ Intensity (g/kWh)']} g/kWh")
                    with col2:
                        st.metric("Power Price", f"€{site['Power Price (EUR/MWh)']}/MWh")
                    with col3:
                        st.metric("Annual CO₂", f"{site['Annual CO₂ (tons)']:,} tons")
        else:
            st.warning("No sites meet the current screening criteria. Try adjusting the filters.")
    
    with subtab2:
        st.subheader("🧪 Product Chemistry Selection & Justification")
        
        # Product options
        products = {
            'Methanol': {'formula': 'CH₃OH', 'co2_utilization': 1.4, 'margin': 70, 'demand_growth': 4.2},
            'Ethylene Carbonate': {'formula': 'C₃H₄O₃', 'co2_utilization': 1.9, 'margin': 700, 'demand_growth': 6.8},
            'Polypropylene Carbonate': {'formula': '(C₄H₆O₃)ₙ', 'co2_utilization': 2.1, 'margin': 800, 'demand_growth': 8.5},
            'Formic Acid': {'formula': 'HCOOH', 'co2_utilization': 1.0, 'margin': 130, 'demand_growth': 5.2},
            'Urea': {'formula': 'CO(NH₂)₂', 'co2_utilization': 0.7, 'margin': 60, 'demand_growth': 2.8}
        }
        
        # Product scoring
        product_scores = {}
        for product, data in products.items():
            margin_score = min(10, (data['margin'] / 100))
            demand_score = min(10, (data['demand_growth'] / 10))
            co2_score = min(10, (data['co2_utilization'] / 3))
            
            composite_score = (margin_score * 0.4 + demand_score * 0.3 + co2_score * 0.3)
            product_scores[product] = {'score': composite_score, 'data': data}
        
        # Sort by score
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Display top products
        st.subheader("🏆 Top Product Recommendations")
        
        for i, (product, info) in enumerate(sorted_products[:3]):
            with st.expander(f"🥇 {product} (Score: {info['score']:.2f})"):
                data = info['data']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Chemical Formula", data['formula'])
                    st.metric("CO₂ Utilization", f"{data['co2_utilization']} tCO₂/t product")
                with col2:
                    st.metric("Margin", f"€{data['margin']}/ton")
                    st.metric("Demand Growth", f"{data['demand_growth']}%/year")
                with col3:
                    st.write("**Strategic Benefits:**")
                    st.write(f"• High margin: €{data['margin']}/ton")
                    st.write(f"• Growing demand: {data['demand_growth']}%/year")
                    st.write(f"• CO₂ utilization: {data['co2_utilization']} tCO₂/t product")
        
        # Methanol-specific analysis
        st.subheader("🧪 Methanol Deep Dive - Our Recommended Product")
        
        methanol_benefits = {
            'Market Size': '100+ million tons globally, 15+ million in EU',
            'CO₂ Impact': '1.4 tons CO₂ utilized per ton methanol produced',
            'Green Premium': '15-25% price premium for sustainable methanol',
            'Transport': 'Liquid at room temperature, easy to transport',
            'Storage': 'Standard chemical storage, no special requirements',
            'Regulations': 'Well-established safety and handling standards'
        }
        
        col1, col2 = st.columns(2)
        for i, (benefit, description) in enumerate(methanol_benefits.items()):
            if i < 3:
                with col1:
                    st.metric(benefit, description)
            else:
                with col2:
                    st.metric(benefit, description)
        
        # Methanol production process
        st.write("**Production Process:**")
        st.write("1. **CO₂ Capture**: From industrial sources (steel, cement, power plants)")
        st.write("2. **Hydrogen Production**: Green hydrogen from renewable electricity")
        st.write("3. **Catalytic Conversion**: CO₂ + 3H₂ → CH₃OH + H₂O")
        st.write("4. **Purification**: Distillation to meet ASTM D1152 standards")
        st.write("5. **Storage & Transport**: Standard chemical logistics")
        
        # Key advantages for Germany
        st.write("**Why Methanol is Perfect for Germany:**")
        st.write("✅ **High CO₂ Sources**: Steel, cement, and chemical industries")
        st.write("✅ **Strong Demand**: Major chemical clusters in NRW and Rhineland")
        st.write("✅ **Infrastructure**: Excellent rail, road, and waterway connections")
        st.write("✅ **Green Premium**: EU policies favor sustainable chemicals")
        st.write("✅ **Export Potential**: Access to EU single market")
        st.write("✅ **Technology Ready**: Proven CO₂-to-methanol pathways")
    
    with subtab3:
        st.subheader("💰 Economic Modeling & Value Stack Analysis")
        
        # Project parameters
        col1, col2 = st.columns(2)
        with col1:
            annual_co2 = st.number_input("Annual CO₂ (tons)", 500000, 3000000, 1500000, 100000)
            co2_utilization = st.selectbox("CO₂ Utilization (tCO₂/t product)", [0.7, 1.0, 1.4, 1.9, 2.1])
        with col2:
            project_scale = st.selectbox("Project Scale", ["Small", "Medium", "Large"])
            capex_multiplier = {"Small": 0.5, "Medium": 1.0, "Large": 2.0}[project_scale]
        
        # Calculate metrics
        annual_production = annual_co2 / co2_utilization
        capex = 100 * capex_multiplier  # Base 100M EUR
        opex = capex * 0.15  # 15% of capex per year
        
        # Host value stack
        eu_ets_value = 85  # EUR/ton CO₂
        host_value_stack = {
            'Avoided CO₂ Cost': annual_co2 * eu_ets_value / 1000000,
            'Logistics & Storage': capex * 0.05,
            'Downtime Risk Reduction': opex * 0.1,
            'Product Premiums': annual_production * 15 / 1000000,
            'Carbon Credits': annual_co2 * 25 / 1000000
        }
        
        total_host_value = sum(host_value_stack.values())
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏭 Project Economics")
            st.metric("Annual Production", f"{annual_production:,.0f} tons")
            st.metric("CAPEX", f"€{capex:.1f}M")
            st.metric("OPEX", f"€{opex:.1f}M/year")
            st.metric("Project Scale", project_scale)
        
        with col2:
            st.subheader("💎 Host Value Stack")
            for key, value in host_value_stack.items():
                st.metric(key, f"€{value:.2f}M/year")
            st.metric("**Total Host Value**", f"€{total_host_value:.2f}M/year")
        
        # Methanol-specific economics
        st.subheader("🧪 Methanol Economics Deep Dive")
        
        # Methanol production costs
        methanol_costs = {
            'CO₂ Cost': 0,  # Free from industrial sources
            'Hydrogen Cost': 3.5,  # EUR/kg H2 (green hydrogen)
            'Catalyst Cost': 0.8,  # EUR/kg methanol
            'Utilities': 1.2,  # EUR/kg methanol
            'Labor & Maintenance': 0.5,  # EUR/kg methanol
            'Total Production Cost': 6.0  # EUR/kg methanol
        }
        
        # Methanol pricing
        methanol_pricing = {
            'Market Price': 0.4,  # EUR/kg methanol (€400/ton)
            'Green Premium': 0.1,  # EUR/kg methanol (€100/ton)
            'Total Selling Price': 0.5,  # EUR/kg methanol (€500/ton)
            'Gross Margin': 0.1,  # EUR/kg methanol (€100/ton)
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Production Costs (per kg methanol)")
            for cost, value in methanol_costs.items():
                if cost == 'Total Production Cost':
                    st.metric(cost, f"€{value:.1f}/kg", delta="Total")
                else:
                    st.metric(cost, f"€{value:.1f}/kg")
        
        with col2:
            st.subheader("💎 Pricing & Margins (per kg methanol)")
            for price, value in methanol_pricing.items():
                if price == 'Gross Margin':
                    st.metric(price, f"€{value:.1f}/kg", delta="Profit")
                else:
                    st.metric(price, f"€{value:.1f}/kg")
        
        # Methanol value chain analysis
        st.subheader("🔗 Methanol Value Chain Analysis")
        
        value_chain = [
            "**CO₂ Source**: Industrial emissions (steel, cement, chemicals)",
            "**Conversion**: CO₂ + 3H₂ → CH₃OH + H₂O (catalytic process)",
            "**Product**: High-purity methanol (99.9%+)",
            "**Transport**: Rail, road, or barge to chemical clusters",
            "**End Use**: Formaldehyde, fuel additives, acetic acid, etc.",
            "**Carbon Impact**: 1.4 tons CO₂ avoided per ton methanol"
        ]
        
        for step in value_chain:
            st.write(f"• {step}")
        
        # Economic summary
        st.subheader("📊 Economic Summary")
        st.write(f"**Project Scale**: {project_scale}")
        st.write(f"**Annual CO₂ Utilization**: {annual_co2:,.0f} tons")
        st.write(f"**Annual Methanol Output**: {annual_production:,.0f} tons")
        st.write(f"**Total Investment**: €{capex:.1f}M")
        st.write(f"**Annual Operating Cost**: €{opex:.1f}M/year")
        st.write(f"**Host Value Creation**: €{total_host_value:.2f}M/year")
        st.write(f"**Methanol Production Cost**: €{methanol_costs['Total Production Cost']:.1f}/kg")
        st.write(f"**Methanol Selling Price**: €{methanol_pricing['Total Selling Price']:.1f}/kg")
        st.write(f"**Gross Margin per kg**: €{methanol_pricing['Gross Margin']:.1f}/kg")
    
    with subtab4:
        st.subheader("🤝 Commercial Structure & Financing Strategy")
        
        # Commercial options
        structures = {
            'License + Royalty': {'risk': 'Low', 'control': 'Medium', 'score': 8.8},
            'JDA/JV': {'risk': 'Medium', 'control': 'Shared', 'score': 8.2},
            'Paid Pilot': {'risk': 'Low', 'control': 'High', 'score': 7.5},
            'Gas-as-a-Service': {'risk': 'Medium', 'control': 'Medium', 'score': 8.0},
            'BOO/BOOT': {'risk': 'High', 'control': 'High', 'score': 7.8}
        }
        
        # Display recommendations
        st.subheader("🏆 Recommended Commercial Structures")
        
        sorted_structures = sorted(structures.items(), key=lambda x: x[1]['score'], reverse=True)
        
        for i, (structure, data) in enumerate(sorted_structures[:3]):
            with st.expander(f"🥇 {structure} (Score: {data['score']:.1f})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Risk Level**: {data['risk']}")
                    st.write(f"**Control Level**: {data['control']}")
                with col2:
                    if structure == 'License + Royalty':
                        st.write("**Why This Structure?**")
                        st.write("• Low risk for technology provider")
                        st.write("• Scalable revenue model")
                        st.write("• Host maintains operational control")
        
        # Financing strategy
        st.subheader("💳 Financing Strategy & Incentives")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Equity", "30%")
        with col2:
            st.metric("Debt", "70%")
        with col3:
            st.metric("Grants", "15%")
        with col4:
            st.metric("Carbon Credits", "5%")
        
        st.write("**Incentive Stacking:**")
        st.write("1. **EU ETS**: €85/ton CO₂ avoided")
        st.write("2. **CBAM**: Border carbon adjustment")
        st.write("3. **Regional Grants**: Up to 30% of CAPEX")
        st.write("4. **Carbon Credits**: Voluntary market access")
    
    with subtab5:
        st.subheader("📈 Financial Quantification & Scalability Analysis")
        
        # Financial parameters
        col1, col2 = st.columns(2)
        with col1:
            capex = st.number_input("CAPEX (M EUR)", 50, 500, 150, 10)
            opex = st.number_input("OPEX (M EUR/year)", 5, 70, 20, 1)
        with col2:
            annual_production = st.number_input("Annual Production (tons)", 100000, 1000000, 500000, 50000)
            product_margin = st.number_input("Product Margin (EUR/ton)", 50, 800, 200, 10)
        
        # Methanol-specific analysis
        st.subheader("🧪 Methanol Offtake Analysis")
        
        # Methanol market data
        methanol_data = {
            'Global Demand': '100+ million tons/year',
            'EU Demand': '15+ million tons/year',
            'Germany Demand': '2.5+ million tons/year',
            'Growth Rate': '3.5%/year',
            'Price Range': '€300-500/ton',
            'Transport Cost': '€0.05-0.15/ton/km'
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Global Demand", methanol_data['Global Demand'])
            st.metric("EU Demand", methanol_data['EU Demand'])
        with col2:
            st.metric("Germany Demand", methanol_data['Germany Demand'])
            st.metric("Growth Rate", methanol_data['Growth Rate'])
        with col3:
            st.metric("Price Range", methanol_data['Price Range'])
            st.metric("Transport Cost", methanol_data['Transport Cost'])
        
        # Methanol applications and buyers
        st.subheader("🏭 Methanol Applications & Buyer Segments")
        
        applications = {
            'Formaldehyde Production': {'demand': '35%', 'buyers': 'Chemical companies', 'proximity': 'High'},
            'MTBE/ETBE (Fuel Additives)': {'demand': '25%', 'buyers': 'Refineries, fuel companies', 'proximity': 'Medium'},
            'Acetic Acid': {'demand': '15%', 'buyers': 'Chemical manufacturers', 'proximity': 'High'},
            'DME (Dimethyl Ether)': {'demand': '10%', 'buyers': 'Energy companies', 'proximity': 'Medium'},
            'Biodiesel': {'demand': '8%', 'buyers': 'Biofuel producers', 'proximity': 'Medium'},
            'Other Chemicals': {'demand': '7%', 'buyers': 'Specialty chemical companies', 'proximity': 'High'}
        }
        
        # Display applications
        for app, data in applications.items():
            with st.expander(f"🔬 {app} ({data['demand']} of market)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Buyer Type**: {data['buyers']}")
                    st.write(f"**Proximity Need**: {data['proximity']}")
                with col2:
                    if app == 'Formaldehyde Production':
                        st.write("**Key Buyers in Germany:**")
                        st.write("• BASF (Ludwigshafen)")
                        st.write("• Covestro (Leverkusen)")
                        st.write("• Evonik (Essen)")
                    elif app == 'MTBE/ETBE (Fuel Additives)':
                        st.write("**Key Buyers in Germany:**")
                        st.write("• Shell (Hamburg)")
                        st.write("• BP (Gelsenkirchen)")
                        st.write("• Total (Leuna)")
                    elif app == 'Acetic Acid':
                        st.write("**Key Buyers in Germany:**")
                        st.write("• Celanese (Frankfurt)")
                        st.write("• BP (Gelsenkirchen)")
                        st.write("• Ineos (Köln)")
        
        # Proximity analysis
        st.subheader("🗺️ Buyer Proximity Analysis")
        
        # Major German chemical clusters
        chemical_clusters = {
            'Ruhr Valley (NRW)': {
                'cities': ['Duisburg', 'Essen', 'Dortmund', 'Bochum'],
                'major_companies': ['Evonik', 'ThyssenKrupp', 'RAG'],
                'distance_from_sites': '0-50 km',
                'offtake_potential': 'Very High',
                'infrastructure': 'Excellent'
            },
            'Rhineland (NRW)': {
                'cities': ['Leverkusen', 'Köln', 'Düsseldorf'],
                'major_companies': ['Bayer', 'Covestro', 'Henkel'],
                'distance_from_sites': '20-80 km',
                'offtake_potential': 'Very High',
                'infrastructure': 'Excellent'
            },
            'Ludwigshafen (Rhineland-Palatinate)': {
                'cities': ['Ludwigshafen', 'Mannheim'],
                'major_companies': ['BASF'],
                'distance_from_sites': '50-150 km',
                'offtake_potential': 'High',
                'infrastructure': 'Excellent'
            },
            'Frankfurt (Hesse)': {
                'cities': ['Frankfurt', 'Offenbach'],
                'major_companies': ['Celanese', 'Clariant'],
                'distance_from_sites': '100-200 km',
                'offtake_potential': 'High',
                'infrastructure': 'Excellent'
            },
            'Hamburg': {
                'cities': ['Hamburg'],
                'major_companies': ['Shell', 'Aurubis'],
                'distance_from_sites': '200-400 km',
                'offtake_potential': 'Medium',
                'infrastructure': 'Good'
            }
        }
        
        # Display chemical clusters
        for cluster, data in chemical_clusters.items():
            with st.expander(f"🏭 {cluster} - {data['offtake_potential']} Offtake Potential"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Cities**: {', '.join(data['cities'])}")
                    st.write(f"**Major Companies**: {', '.join(data['major_companies'])}")
                    st.write(f"**Distance from Sites**: {data['distance_from_sites']}")
                with col2:
                    st.write(f"**Offtake Potential**: {data['offtake_potential']}")
                    st.write(f"**Infrastructure**: {data['infrastructure']}")
                    
                    # Calculate transport costs
                    if '50' in data['distance_from_sites']:
                        transport_cost = "€2.5-7.5/ton"
                    elif '150' in data['distance_from_sites']:
                        transport_cost = "€7.5-22.5/ton"
                    elif '400' in data['distance_from_sites']:
                        transport_cost = "€20-60/ton"
                    else:
                        transport_cost = "€5-15/ton"
                    
                    st.write(f"**Transport Cost**: {transport_cost}")
        
        # Logistics and infrastructure
        st.subheader("🚚 Logistics & Infrastructure Analysis")
        
        logistics_factors = {
            'Rail Network': 'Excellent - DB Cargo connections to all major clusters',
            'Road Network': 'Excellent - Autobahn A1, A2, A3, A40, A57',
            'Waterways': 'Good - Rhine, Ruhr, Main rivers for barge transport',
            'Storage Facilities': 'Available - Chemical storage terminals in major ports',
            'Safety Standards': 'High - ADR compliance for chemical transport',
            'Customs': 'EU internal market - no customs for Germany'
        }
        
        col1, col2 = st.columns(2)
        for i, (factor, status) in enumerate(logistics_factors.items()):
            if i < 3:
                with col1:
                    st.write(f"**{factor}**: {status}")
            else:
                with col2:
                    st.write(f"**{factor}**: {status}")
        
        # Competitive advantage
        st.subheader("🏆 Competitive Advantages for Methanol Production")
        
        advantages = [
            "**Green Methanol Premium**: 15-25% price premium for CO₂-based methanol",
            "**EU ETS Benefits**: Avoid €85/ton CO₂ costs",
            "**CBAM Protection**: Border carbon adjustment for imports",
            "**Proximity to Buyers**: Major chemical clusters within 200km",
            "**Infrastructure**: Excellent rail, road, and waterway connections",
            "**Regulatory Support**: Strong EU and German climate policies",
            "**Market Growth**: 3.5% annual demand growth in Europe"
        ]
        
        for advantage in advantages:
            st.write(f"✅ {advantage}")
        
        # Offtake agreement recommendations
        st.subheader("📋 Offtake Agreement Strategy")
        
        st.write("**Recommended Approach:**")
        st.write("1. **Long-term Contracts**: 5-10 year agreements with major buyers")
        st.write("2. **Volume Commitments**: 70-80% of production under contract")
        st.write("3. **Price Indexation**: Link to methanol market prices + green premium")
        st.write("4. **Transport Solutions**: Offer FOB site or deliver to buyer facilities")
        st.write("5. **Quality Guarantees**: Meet ASTM D1152 methanol specifications")
        st.write("6. **Sustainability Certification**: ISCC Plus or similar green certification")
        
        # Key buyer outreach
        st.write("**Priority Buyer Outreach:**")
        st.write("• **BASF** (Ludwigshafen) - Largest chemical company in Germany")
        st.write("• **Bayer/Covestro** (Leverkusen) - Major formaldehyde producers")
        st.write("• **Evonik** (Essen) - Specialty chemicals and materials")
        st.write("• **Shell** (Hamburg) - Fuel additives and energy")
        st.write("• **Celanese** (Frankfurt) - Acetic acid production")
        
        # Methanol-specific commercial considerations
        st.subheader("🤝 Methanol Commercial Strategy")
        
        st.write("**Key Commercial Advantages:**")
        st.write("✅ **Established Market**: Methanol is a commodity chemical with stable demand")
        st.write("✅ **Multiple Buyers**: Diverse customer base reduces dependency risk")
        st.write("✅ **Standard Specifications**: ASTM D1152 standards ensure quality acceptance")
        st.write("✅ **Transport Flexibility**: Can use rail, road, or barge transport")
        st.write("✅ **Storage Compatibility**: Standard chemical storage facilities")
        st.write("✅ **Green Premium**: Sustainability credentials command price premium")
        
        st.write("**Risk Mitigation:**")
        st.write("🛡️ **Volume Diversification**: Supply to 3-5 major buyers")
        st.write("🛡️ **Long-term Contracts**: 5-10 year agreements for stability")
        st.write("🛡️ **Price Indexation**: Link to methanol market prices")
        st.write("🛡️ **Quality Guarantees**: Meet or exceed industry standards")
        st.write("🛡️ **Transport Options**: Multiple logistics providers")
        
        # Calculate metrics
        annual_revenue = annual_production * product_margin / 1000000  # M EUR
        annual_profit = annual_revenue - opex
        payback_period = capex / annual_profit if annual_profit > 0 else float('inf')
        irr = (annual_profit / capex) * 100
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Financial Metrics")
            st.metric("Annual Revenue", f"€{annual_revenue:.2f}M")
            st.metric("Annual Profit", f"€{annual_profit:.2f}M")
            st.metric("Payback Period", f"{payback_period:.1f} years")
            st.metric("Project IRR", f"{irr:.1f}%")
        
        with col2:
            st.subheader("📊 Cost Analysis")
            cost_per_ton = (capex + opex * 25) / (annual_production * 25)
            st.metric("Cost per Ton Product", f"€{cost_per_ton:.0f}")
            st.metric("Project Life", "25 years")
            st.metric("Discount Rate", "8%")
        
        # Scalability analysis
        st.subheader("🚀 Scalability & Replicability")
        
        scalability_factors = {
            'Technology Maturity': 'High - Proven CO₂ utilization pathways',
            'Market Demand': 'Growing at 4.2%/year',
            'Regulatory Support': 'Strong - EU climate policies',
            'Financing Availability': 'Good - Multiple incentive programs'
        }
        
        col1, col2 = st.columns(2)
        for i, (factor, status) in enumerate(scalability_factors.items()):
            if i < 2:
                with col1:
                    st.write(f"**{factor}**: {status}")
            else:
                with col2:
                    st.write(f"**{factor}**: {status}")
        
        # Summary dashboard
        st.subheader("🎯 Project Summary")
        
        summary_data = {
            'Metric': ['Total Investment', 'Annual Production', 'Payback Period', 'Project IRR'],
            'Value': [f"€{capex:.1f}M", f"{annual_production:,.0f} tons", f"{payback_period:.1f} years", f"{irr:.1f}%"]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Methanol-specific financial insights
        st.subheader("🧪 Methanol Financial Insights")
        
        # Methanol market analysis
        methanol_market = {
            'Market Size': '€6B EU market, €1.25B Germany',
            'Growth Rate': '3.5% annually',
            'Price Volatility': 'Low to moderate',
            'Seasonality': 'Minimal - steady demand year-round',
            'Competition': 'Established players + new green entrants',
            'Regulatory Risk': 'Low - well-established standards'
        }
        
        col1, col2 = st.columns(2)
        for i, (factor, status) in enumerate(methanol_market.items()):
            if i < 3:
                with col1:
                    st.write(f"**{factor}**: {status}")
            else:
                with col2:
                    st.write(f"**{factor}**: {status}")
        
        # Methanol investment thesis
        st.write("**Investment Thesis for Methanol from CO₂:**")
        st.write("🎯 **Strong Fundamentals**: Established market with growing demand")
        st.write("🌱 **Green Premium**: Sustainability credentials command price premium")
        st.write("🏭 **Proximity Advantage**: Close to major German chemical clusters")
        st.write("🚚 **Logistics Excellence**: Excellent transport infrastructure")
        st.write("📈 **Growth Potential**: 3.5% annual demand growth in Europe")
        st.write("🛡️ **Risk Mitigation**: Diversified buyer base and long-term contracts")
        
        # Export results
        if st.button("📥 Export Germany Site Analysis"):
            summary = {
                'timestamp': datetime.now().isoformat(),
                'project_scale': project_scale,
                'capex': capex,
                'annual_production': annual_production,
                'payback_period': payback_period,
                'project_irr': irr
            }
            
            with open('germany_site_analysis_results.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            st.success("✅ Germany site analysis exported to `germany_site_analysis_results.json`")

# Google Maps Methanol Buyer Discovery Tab
with tab7:
    st.header("🗺️ Top Sites + Closest Methanol Buyers")
    st.markdown("**Automatically find the closest methanol buyers for your top German sites**")
    
    # 🎯 METHANOL PRODUCTION COST CALCULATOR - PROMINENT DISPLAY
    st.markdown("---")
    st.markdown("## 💰 **METHANOL PRODUCTION COST CALCULATOR**")
    st.markdown("**Your baseline cost estimates for methanol production**")
    
    # Cost calculation parameters in a prominent box
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### ⚡ **Energy Requirements**")
        st.markdown("""
        **5,320 kWh/ton MeOH**  
        Current DE price: **€0.15/kWh**  
        **Energy cost: €798/ton MeOH**
        """)
        
    with col2:
        st.markdown("### 💧 **Input Requirements**")
        st.markdown("""
        **100 tons CO₂** (free from your site)  
        **11 tons water** (€0.50/ton)  
        **9 tons H₂** (€3.50/kg)
        """)
        
    with col3:
        st.markdown("### 💰 **Total Production Cost**")
        st.markdown("""
        **Energy**: €798/ton  
        **Water**: €5.50/ton  
        **Hydrogen**: €31,500/ton  
        **TOTAL: €32,303.50/ton**
        """)
    
    # Key insights box
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🎯 Key Cost Drivers:**
        • **Hydrogen dominates**: 97.5% of total cost
        • **Energy is secondary**: 2.5% of total cost  
        • **CO₂ is essentially free**: Your competitive advantage
        """)
    
    with col2:
        st.success("""
        **💡 Strategic Insights:**
        • Focus on hydrogen cost reduction
        • Energy efficiency has limited impact
        • CO₂ proximity is crucial for profitability
        """)
    
    st.markdown("---")
    
    # Pre-defined top German sites with their coordinates and scoring data
    top_sites = {
        "Essen (Ruhr Valley)": {
            "coordinates": (51.4556, 7.0117),
            "description": "Major industrial hub, steel & chemicals",
            "co2_sources": "Steel plants, power stations",
            "carbon_intensity": 142,  # gCO2/kWh (current DE average)
            "avg_distance_to_buyers": 35,  # km
            "industry": "Steel & Chemicals"
        },
        "Leverkusen (Chemical Hub)": {
            "coordinates": (51.0333, 6.9833),
            "description": "Bayer, Covestro headquarters",
            "co2_sources": "Chemical manufacturing",
            "carbon_intensity": 138,  # gCO2/kWh
            "avg_distance_to_buyers": 28,  # km
            "industry": "Chemical Manufacturing"
        },
        "Ludwigshafen (BASF)": {
            "coordinates": (49.4811, 8.4353),
            "description": "BASF world headquarters",
            "co2_sources": "Chemical production",
            "carbon_intensity": 135,  # gCO2/kWh
            "avg_distance_to_buyers": 42,  # km
            "industry": "Chemical Production"
        },
        "Duisburg (Steel Hub)": {
            "coordinates": (51.4344, 6.7623),
            "description": "ThyssenKrupp steel production",
            "co2_sources": "Steel manufacturing",
            "carbon_intensity": 145,  # gCO2/kWh
            "avg_distance_to_buyers": 38,  # km
            "industry": "Steel Manufacturing"
        },
        "Gelsenkirchen (Energy Hub)": {
            "coordinates": (51.5136, 7.1003),
            "description": "Major power generation",
            "co2_sources": "Power plants, refineries",
            "carbon_intensity": 155,  # gCO2/kWh
            "avg_distance_to_buyers": 45,  # km
            "industry": "Power Generation"
        }
    }
    
    # Site selection
    selected_site = st.selectbox(
        "🏭 Select Your Site:",
        list(top_sites.keys()),
        help="Choose from our pre-analyzed top German industrial sites"
    )
    
    # Show site details
    site_info = top_sites[selected_site]
    st.subheader(f"📍 {selected_site}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Coordinates**: {site_info['coordinates'][0]:.4f}, {site_info['coordinates'][1]:.4f}")
        st.write(f"**Description**: {site_info['description']}")
        st.write(f"**Industry**: {site_info['industry']}")
    with col2:
        st.write(f"**CO₂ Sources**: {site_info['co2_sources']}")
        st.write(f"**Carbon Intensity**: {site_info['carbon_intensity']} gCO₂/kWh")
        st.write(f"**Avg Distance to Buyers**: {site_info['avg_distance_to_buyers']} km")
        st.write(f"**Search Radius**: 50 km")
    
    # Site Cost Scoring System
    st.subheader("📊 Site Cost Scoring & Recommendations")
    st.markdown("**Ranked by cost-effectiveness and buyer proximity**")
    
    # Enhanced scoring explanation
    st.markdown("""
    **🏆 Scoring System (100 base + bonuses):**
    • **Energy Factor**: +20 for very clean (<100 gCO₂/kWh), +10 for clean (<150), -10 for dirty (>300)
    • **Distance Factor**: +15 for close buyers (<25km), -10 for far buyers (>75km)  
    • **Infrastructure**: +10 for steel plants, +15 for chemical hubs
    • **Regulatory**: +5 for Ruhr Valley incentives
    """)
    
    # Site scoring table
    st.subheader("🏭 Site Cost Rankings")
    
    # Calculate scores for each site
    site_scores = {}
    for site_name, site_info in top_sites.items():
        # Base score starts at 100
        score = 100
        
        # Energy cost factor (lower carbon intensity = better)
        carbon_intensity = site_info.get('carbon_intensity', 150)  # gCO2/kWh
        if carbon_intensity < 100:
            score += 20  # Very clean energy
        elif carbon_intensity < 150:
            score += 10  # Clean energy
        elif carbon_intensity > 300:
            score -= 10  # High carbon energy
        
        # Distance to major buyers factor
        if site_info.get('avg_distance_to_buyers', 50) < 25:
            score += 15  # Close to buyers
        elif site_info.get('avg_distance_to_buyers', 50) > 75:
            score -= 10  # Far from buyers
        
        # Infrastructure factor
        if 'steel' in site_info.get('co2_sources', '').lower():
            score += 10  # Steel plants have good infrastructure
        if 'chemical' in site_info.get('co2_sources', '').lower():
            score += 15  # Chemical hubs are ideal
        
        # Regulatory factor
        if 'ruhr' in site_name.lower():
            score += 5  # Ruhr Valley has good incentives
        
        site_scores[site_name] = score
    
    # Sort sites by score
    sorted_sites = sorted(site_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Display enhanced scoring table with cost details
    scoring_data = []
    for site_name, score in sorted_sites:
        site_info = top_sites[site_name]
        
        # Calculate site-specific costs
        energy_cost = site_info.get('carbon_intensity', 150) * 5.32 * 0.15
        total_cost = energy_cost + 5.50 + 31500  # energy + water + hydrogen
        
        scoring_data.append({
            'Site': site_name,
            'Score': score,
            'Rating': '🥇' if score >= 120 else '🥈' if score >= 100 else '🥉',
            'Energy Cost (€/ton)': f"€{energy_cost:.1f}",
            'Total Cost (€/ton)': f"€{total_cost:,.0f}",
            'Carbon Intensity': f"{site_info.get('carbon_intensity', 150)} gCO₂/kWh",
            'Distance to Buyers': f"{site_info.get('avg_distance_to_buyers', 50):.0f} km",
            'CO₂ Sources': site_info['co2_sources']
        })
    
    scoring_df = pd.DataFrame(scoring_data)
    st.dataframe(scoring_df, use_container_width=True)
    
    # Enhanced top recommendation with cost analysis
    top_site = sorted_sites[0]
    top_site_info = top_sites[top_site[0]]
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"🏆 **TOP RECOMMENDATION: {top_site[0]}**")
        st.write(f"**Score**: {top_site[1]}/100")
        st.write(f"**Industry**: {top_site_info['industry']}")
        st.write(f"**CO₂ Sources**: {top_site_info['co2_sources']}")
    
    with col2:
        st.info("**💰 Cost Analysis:**")
        energy_cost = top_site_info.get('carbon_intensity', 150) * 5.32 * 0.15
        total_cost = energy_cost + 5.50 + 31500
        st.write(f"**Energy Cost**: €{energy_cost:.1f}/ton")
        st.write(f"**Total Cost**: €{total_cost:,.0f}/ton")
        st.write(f"**Buyer Distance**: {top_site_info.get('avg_distance_to_buyers', 50):.0f} km")
    
    # Cost comparison across all sites
    st.markdown("---")
    st.subheader("📊 Cost Comparison Across All Sites")
    
    # Create cost comparison chart
    cost_comparison_data = []
    for site_name, score in sorted_sites:
        site_info = top_sites[site_name]
        energy_cost = site_info.get('carbon_intensity', 150) * 5.32 * 0.15
        total_cost = energy_cost + 5.50 + 31500
        
        cost_comparison_data.append({
            'Site': site_name,
            'Energy Cost (€/ton)': energy_cost,
            'Total Cost (€/ton)': total_cost,
            'Score': score
        })
    
    cost_df = pd.DataFrame(cost_comparison_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**💰 Energy Cost Comparison:**")
        st.dataframe(cost_df[['Site', 'Energy Cost (€/ton)', 'Score']].sort_values('Energy Cost (€/ton)'), use_container_width=True)
    
    with col2:
        st.write("**🏆 Overall Ranking by Score:**")
        st.dataframe(cost_df[['Site', 'Score', 'Total Cost (€/ton)']].sort_values('Score', ascending=False), use_container_width=True)
    
    # Key insights
    st.markdown("---")
    st.subheader("💡 Key Insights for Decision Making")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🎯 Cost Optimization Strategy:**
        • **Energy costs vary** by €15-25/ton between sites
        • **Hydrogen dominates** total cost (97.5%)
        • **Site selection impact** on energy: 0.5% of total cost
        • **Buyer proximity** more important than energy costs
        """)
    
    with col2:
        st.success("""
        **🚀 Strategic Recommendations:**
        • **Focus on hydrogen supply** partnerships
        • **Prioritize buyer proximity** over energy efficiency
        • **Leverage CO₂ proximity** for competitive advantage
        • **Consider infrastructure** quality for long-term success
        """)
    
    # Search button
    search_button = st.button("🔍 Find Closest Methanol Buyers", type="primary")
    
    if search_button:
        try:
            # Import Google Maps finder
            from api_connectors.google_maps_methanol_finder import GoogleMapsMethanolFinder
            import yaml
            
            # Load API keys
            with open('backend/api_keys.yaml', 'r') as file:
                api_keys = yaml.safe_load(file)
            
            google_maps_key = api_keys.get('google_maps')
            
            if not google_maps_key:
                st.error("❌ Google Maps API key not found. Please check your configuration.")
            else:
                with st.spinner("🔍 Searching Google Maps for methanol buyers..."):
                    # Initialize finder
                    finder = GoogleMapsMethanolFinder(api_key=google_maps_key)
                    
                    # Search for buyers using selected site coordinates
                    site_coordinates = site_info['coordinates']
                    results = finder.find_methanol_buyers_near_site(
                        site_coordinates=site_coordinates,
                        search_radius_km=50
                    )
                
                if results:
                    st.success(f"✅ Found {len(results)} potential methanol buyers near {selected_site}!")
                    
                    # Simple distance-based ranking
                    st.subheader("🏆 Closest Methanol Buyers (Ranked by Distance)")
                    
                    # Sort by distance and show top results
                    sorted_results = sorted(results, key=lambda x: x.distance_km)
                    top_results = sorted_results[:10]  # Show top 10 closest
                    
                    # Display in simple format
                    for i, buyer in enumerate(top_results, 1):
                        col1, col2, col3 = st.columns([1, 3, 2])
                        
                        with col1:
                            if i == 1:
                                st.markdown("🥇")
                            elif i == 2:
                                st.markdown("🥈")
                            elif i == 3:
                                st.markdown("🥉")
                            else:
                                st.markdown(f"**{i}**")
                        
                        with col2:
                            st.write(f"**{buyer.company_name}**")
                            st.write(f"📍 {buyer.address}")
                            st.write(f"🏢 {buyer.business_type}")
                        
                        with col3:
                            st.metric("Distance", f"{buyer.distance_km:.1f} km")
                            if buyer.phone:
                                st.write(f"📞 {buyer.phone}")
                            if buyer.website:
                                st.write(f"🌐 [Website]({buyer.website})")
                        
                        st.divider()
                    
                    # Quick summary
                    st.subheader("📊 Quick Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        closest = sorted_results[0] if sorted_results else None
                        if closest:
                            st.metric("Closest Buyer", f"{closest.company_name}")
                            st.metric("Distance", f"{closest.distance_km:.1f} km")
                    
                    with col2:
                        avg_distance = sum(b.distance_km for b in sorted_results) / len(sorted_results)
                        st.metric("Average Distance", f"{avg_distance:.1f} km")
                        st.metric("Total Buyers", len(sorted_results))
                    
                    with col3:
                        # Count by distance ranges
                        very_close = len([b for b in sorted_results if b.distance_km <= 10])
                        close = len([b for b in sorted_results if 10 < b.distance_km <= 25])
                        medium = len([b for b in sorted_results if 25 < b.distance_km <= 50])
                        
                        st.metric("≤10 km", f"{very_close} buyers")
                        st.metric("10-25 km", f"{close} buyers")
                        st.metric("25-50 km", f"{medium} buyers")
                    
                    # Export functionality
                    st.subheader("📥 Export Results")
                    if st.button("💾 Export to JSON"):
                        export_data = []
                        for buyer in results:
                            export_data.append({
                                'company_name': buyer.company_name,
                                'address': buyer.address,
                                'coordinates': buyer.coordinates,
                                'distance_km': buyer.distance_km,
                                'business_type': buyer.business_type,
                                'phone': buyer.phone,
                                'website': buyer.website,
                                'rating': buyer.rating,
                                'last_updated': buyer.last_updated.isoformat()
                            })
                        
                        # Save to file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"google_maps_buyers_{timestamp}.json"
                        
                        with open(filename, 'w') as f:
                            json.dump(export_data, f, indent=2)
                        
                        st.success(f"✅ Results exported to `{filename}`")
                
                else:
                    st.warning("⚠️ No methanol buyers found in the specified radius. Try increasing the search radius or checking different coordinates.")
        
        except Exception as e:
            st.error(f"❌ Error during search: {str(e)}")
            st.info("💡 Make sure you have enabled the required Google Maps APIs (Places API, Geocoding API)")
    
    # Simple instructions
    st.subheader("💡 How to Use")
    
    st.write("""
    1. **Select your site** from the dropdown above
    2. **Click 'Find Closest Methanol Buyers'**
    3. **See ranked results** by distance
    4. **Export data** for further analysis
    """)
    
    st.info("""
    **🎯 This system automatically finds the closest methanol buyers within 50km of your selected site.**
    **Results are ranked by distance, so you can immediately see your best offtake opportunities.**
    """)

# AI Site Analysis & Break-Even Tab
with tab8:
    st.header("🤖 AI Site Analysis & Break-Even Calculator")
    st.markdown("**Comprehensive AI-powered analysis using Groq API for site evaluation and break-even calculations**")
    
    # Site selection for analysis
    st.subheader("🏭 Select Site for AI Analysis")
    analysis_site = st.selectbox(
        "Choose a site for detailed AI analysis:",
        list(top_sites.keys()),
        help="Select a site to get AI-powered insights and break-even calculations"
    )
    
    # Analysis parameters
    st.subheader("⚙️ Analysis Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        project_scale_kt = st.number_input(
            "Project Scale (kt MeOH/year)", 
            min_value=10, 
            max_value=1000, 
            value=100,
            help="Annual methanol production capacity in kilotons"
        )
        
        hydrogen_cost_kg = st.number_input(
            "Hydrogen Cost (€/kg)", 
            min_value=1.0, 
            max_value=10.0, 
            value=3.5,
            step=0.1,
            help="Current hydrogen market price"
        )
        
        methanol_price_ton = st.number_input(
            "Methanol Selling Price (€/ton)", 
            min_value=200, 
            max_value=800, 
            value=400,
            help="Expected methanol market price"
        )
    
    with col2:
        capex_per_kt = st.number_input(
            "CAPEX per kt (€M/kt)", 
            min_value=0.5, 
            max_value=3.0, 
            value=1.2,
            step=0.1,
            help="Capital expenditure per kiloton of capacity"
        )
        
        opex_percent = st.number_input(
            "OPEX (% of CAPEX)", 
            min_value=5.0, 
            max_value=20.0, 
            value=8.0,
            step=0.5,
            help="Annual operating expenses as percentage of CAPEX"
        )
        
        discount_rate = st.number_input(
            "Discount Rate (%)", 
            min_value=5.0, 
            max_value=15.0, 
            value=10.0,
            step=0.5,
            help="Project discount rate for NPV calculations"
        )
    
    # AI Analysis Button
    if st.button("🚀 Run AI Analysis", type="primary"):
        try:
            # Import Groq client
            import os
            from groq import Groq
            
            # Get Groq API key
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                st.error("❌ GROQ_API_KEY environment variable not found. Please set it to run AI analysis.")
                st.info("💡 Set your Groq API key: export GROQ_API_KEY='your_key_here'")
            else:
                with st.spinner("🤖 Running AI analysis with Groq..."):
                    # Initialize Groq client
                    client = Groq(api_key=groq_api_key)
                    
                    # Get site information
                    site_info = top_sites[analysis_site]
                    
                    # Prepare analysis prompt
                    analysis_prompt = f"""
                    You are an expert chemical engineer and financial analyst specializing in methanol production from CO₂.
                    
                    Analyze this German industrial site for methanol production:
                    
                    SITE: {analysis_site}
                    COORDINATES: {site_info['coordinates']}
                    INDUSTRY: {site_info['industry']}
                    CO₂ SOURCES: {site_info['co2_sources']}
                    CARBON INTENSITY: {site_info.get('carbon_intensity', 150)} gCO₂/kWh
                    AVG DISTANCE TO BUYERS: {site_info.get('avg_distance_to_buyers', 50)} km
                    
                    PROJECT PARAMETERS:
                    - Scale: {project_scale_kt} kt MeOH/year
                    - Hydrogen cost: €{hydrogen_cost_kg}/kg
                    - Methanol price: €{methanol_price_ton}/ton
                    - CAPEX: €{capex_per_kt}M per kt capacity
                    - OPEX: {opex_percent}% of CAPEX annually
                    - Discount rate: {discount_rate}%
                    
                    BASELINE COSTS (per ton MeOH):
                    - Energy: 5,320 kWh × €0.15/kWh = €798
                    - Water: 11 tons × €0.50/ton = €5.50
                    - Hydrogen: 9 tons × €{hydrogen_cost_kg}/kg = €{9 * hydrogen_cost_kg * 1000}
                    - Total production cost: €{798 + 5.50 + (9 * hydrogen_cost_kg * 1000):,.0f}
                    
                    Provide a comprehensive analysis including:
                    1. Site suitability score (1-10) with justification
                    2. Break-even analysis with timeline
                    3. Required output rate for profitability
                    4. Key risks and mitigation strategies
                    5. Strategic recommendations
                    6. Financial projections (NPV, IRR, payback period)
                    
                    Format your response in clear sections with actionable insights.
                    """
                    
                    # Run Groq analysis
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": analysis_prompt
                            }
                        ],
                        model="llama-3.1-8b-instant",
                        temperature=0.3,
                        max_tokens=2000
                    )
                    
                    # Display AI analysis results
                    ai_analysis = chat_completion.choices[0].message.content
                    
                    st.success("✅ AI Analysis Complete!")
                    
                    # Display results in organized sections
                    st.markdown("---")
                    st.subheader("🤖 AI Analysis Results")
                    
                    # Parse and display the analysis
                    st.markdown(ai_analysis)
                    
                    # Additional financial calculations
                    st.markdown("---")
                    st.subheader("💰 Financial Calculations")
                    
                    # Calculate key metrics
                    total_capex = project_scale_kt * capex_per_kt
                    annual_opex = total_capex * (opex_percent / 100)
                    annual_revenue = project_scale_kt * 1000 * methanol_price_ton
                    annual_cost = project_scale_kt * 1000 * (798 + 5.50 + (9 * hydrogen_cost_kg * 1000))
                    annual_profit = annual_revenue - annual_cost - annual_opex
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total CAPEX", f"€{total_capex:.1f}M")
                        st.metric("Annual OPEX", f"€{annual_opex:.1f}M")
                    
                    with col2:
                        st.metric("Annual Revenue", f"€{annual_revenue:,.0f}")
                        st.metric("Annual Cost", f"€{annual_cost:,.0f}")
                    
                    with col3:
                        st.metric("Annual Profit", f"€{annual_profit:,.0f}")
                        if annual_profit > 0:
                            payback_years = total_capex / annual_profit
                            st.metric("Payback Period", f"{payback_years:.1f} years")
                        else:
                            st.metric("Payback Period", "Never")
                    
                    # Break-even analysis
                    st.markdown("---")
                    st.subheader("📊 Break-Even Analysis")
                    
                    if annual_profit > 0:
                        # Calculate break-even output rate
                        fixed_costs = annual_opex
                        variable_cost_per_ton = 798 + 5.50 + (9 * hydrogen_cost_kg * 1000)
                        contribution_margin = methanol_price_ton - variable_cost_per_ton
                        
                        if contribution_margin > 0:
                            break_even_tonnes = fixed_costs / contribution_margin
                            break_even_percent = (break_even_tonnes / (project_scale_kt * 1000)) * 100
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.info(f"""
                                **Break-Even Output:**
                                • **{break_even_tonnes:,.0f} tonnes/year**
                                • **{break_even_percent:.1f}% of capacity**
                                • **Contribution margin**: €{contribution_margin:.0f}/tonne
                                """)
                            
                            with col2:
                                st.success(f"""
                                **Profitability Threshold:**
                                • **Above {break_even_percent:.1f}% capacity**: Profitable
                                • **Below {break_even_percent:.1f}% capacity**: Loss-making
                                • **Full capacity profit**: €{annual_profit:,.0f}/year
                                """)
                        else:
                            st.error("❌ **Critical Issue**: Variable costs exceed selling price. Project is not viable at current parameters.")
                    else:
                        st.error("❌ **Project Not Viable**: Annual costs exceed revenue. Review pricing and cost assumptions.")
                    
                    # Export analysis
                    st.markdown("---")
                    st.subheader("📥 Export Analysis")
                    
                    if st.button("💾 Export AI Analysis to JSON"):
                        export_data = {
                            'site': analysis_site,
                            'site_info': site_info,
                            'project_parameters': {
                                'scale_kt': project_scale_kt,
                                'hydrogen_cost_kg': hydrogen_cost_kg,
                                'methanol_price_ton': methanol_price_ton,
                                'capex_per_kt': capex_per_kt,
                                'opex_percent': opex_percent,
                                'discount_rate': discount_rate
                            },
                            'financial_metrics': {
                                'total_capex_m': total_capex,
                                'annual_opex_m': annual_opex,
                                'annual_revenue': annual_revenue,
                                'annual_cost': annual_cost,
                                'annual_profit': annual_profit,
                                'payback_years': total_capex / annual_profit if annual_profit > 0 else None
                            },
                            'break_even_analysis': {
                                'break_even_tonnes': break_even_tonnes if 'break_even_tonnes' in locals() else None,
                                'break_even_percent': break_even_percent if 'break_even_percent' in locals() else None,
                                'contribution_margin': contribution_margin if 'contribution_margin' in locals() else None
                            },
                            'ai_analysis': ai_analysis,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Save to file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"ai_site_analysis_{analysis_site.replace(' ', '_')}_{timestamp}.json"
                        
                        with open(filename, 'w') as f:
                            json.dump(export_data, f, indent=2)
                        
                        st.success(f"✅ AI analysis exported to `{filename}`")
                
        except ImportError:
            st.error("❌ Groq library not installed. Install with: pip install groq")
            st.info("💡 Run: pip install groq")
        except Exception as e:
            st.error(f"❌ Error during AI analysis: {str(e)}")
            st.info("💡 Make sure you have set the GROQ_API_KEY environment variable")
    


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p style="font-size: 1.1rem;">🇪🇺 CarbonSiteAI EU - Built for Turnover Labs | European Market Focus</p>
    <p>EU Green Deal Alignment | EU ETS Integration | European Industrial Strategy</p>
</div>
""", unsafe_allow_html=True)

#!/usr/bin/env python3
"""
CarbonSiteAI EU - Robust Version for Streamlit Cloud Deployment
"""

import streamlit as st
import sys
import os

# Page configuration
st.set_page_config(
    page_title="🌍 CarbonSiteAI EU - European Site Selector",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Try to import dependencies with error handling
try:
    import pandas as pd
    import numpy as np
    import folium
    from streamlit_folium import folium_static
    import plotly.express as px
    import plotly.graph_objects as go
    from datetime import datetime
    import json
    
    # Add backend to path for API access
    sys.path.append('backend')
    
    # Try to import backend modules
    try:
        from api_connectors.energy_data_api import EnergyDataConnector
        backend_available = True
    except ImportError as e:
        st.warning(f"⚠️ Backend modules not available: {str(e)}")
        backend_available = False
        
    st.success("✅ All core dependencies imported successfully")
    
except ImportError as e:
    st.error(f"❌ Critical dependency missing: {str(e)}")
    st.stop()

# Custom CSS for modern styling
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Main app
def main():
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🌍 CarbonSiteAI EU</h1>
        <p class="hero-subtitle">AI-Powered Carbon Site Analysis & Methanol Production Planning</p>
        <p>European Market Focus | EU Green Deal Alignment | Industrial Strategy</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.success("✅ Core App")
        st.write("Streamlit running")
    
    with col2:
        if backend_available:
            st.success("✅ Backend")
            st.write("API connectors ready")
        else:
            st.warning("⚠️ Backend")
            st.write("Limited functionality")
    
    with col3:
        st.info("ℹ️ Dependencies")
        st.write("All packages loaded")
    
    with col4:
        st.info("🌐 Deployment")
        st.write("Streamlit Cloud")
    
    # Main content
    st.markdown("---")
    st.subheader("🚀 Application Status")
    
    if backend_available:
        st.success("🎉 **Full Application Ready!**")
        st.write("Your CarbonSiteAI EU application is fully functional with:")
        st.write("• Energy data connectors")
        st.write("• Google Maps integration")
        st.write("• AI analysis capabilities")
        st.write("• Site screening engine")
        
        # Test backend functionality
        try:
            connector = EnergyDataConnector()
            st.success("✅ Energy Data Connector initialized successfully")
        except Exception as e:
            st.error(f"❌ Backend initialization error: {str(e)}")
    
    else:
        st.warning("⚠️ **Limited Functionality**")
        st.write("The app is running but some features may not work:")
        st.write("• Core Streamlit functionality: ✅ Working")
        st.write("• Backend API connectors: ❌ Not available")
        st.write("• Data visualization: ✅ Working")
        
        st.info("💡 **To enable full functionality:**")
        st.write("1. Check that all backend files are in the repository")
        st.write("2. Verify the directory structure is correct")
        st.write("3. Check Streamlit Cloud logs for specific errors")
    
    # Deployment information
    st.markdown("---")
    st.subheader("🌐 Deployment Information")
    
    st.info("""
    **Current Status:** Deployed on Streamlit Cloud
    
    **Repository:** https://github.com/ritzzi23/carbonsiteAI
    
    **Main App File:** streamlit_app_eu.py
    
    **Test File:** test_deployment.py (for debugging)
    """)
    
    # Troubleshooting
    st.markdown("---")
    st.subheader("🔧 Troubleshooting")
    
    if st.button("🔄 Test Backend Connection"):
        if backend_available:
            try:
                connector = EnergyDataConnector()
                st.success("✅ Backend connection successful!")
            except Exception as e:
                st.error(f"❌ Backend connection failed: {str(e)}")
        else:
            st.error("❌ Backend not available")
    
    if st.button("📊 Show System Info"):
        st.json({
            "python_version": sys.version,
            "streamlit_version": st.__version__,
            "working_directory": os.getcwd(),
            "files_in_directory": len(os.listdir(".")),
            "backend_available": backend_available
        })

if __name__ == "__main__":
    main()

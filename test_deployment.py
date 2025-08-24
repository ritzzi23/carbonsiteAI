#!/usr/bin/env python3
"""
Simple test file to check deployment issues
"""

import streamlit as st

st.set_page_config(
    page_title="Test App",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Test App - CarbonSiteAI EU")
st.write("This is a simple test to check if Streamlit Cloud deployment works.")

# Test basic functionality
st.success("✅ Basic Streamlit functionality working")

# Test if we can import backend modules
try:
    import sys
    sys.path.append('backend')
    from api_connectors.energy_data_api import EnergyDataConnector
    st.success("✅ Backend imports working")
except Exception as e:
    st.error(f"❌ Backend import error: {str(e)}")

# Test if we can import other dependencies
try:
    import pandas as pd
    import numpy as np
    import folium
    import plotly.express as px
    st.success("✅ All dependencies imported successfully")
except Exception as e:
    st.error(f"❌ Dependency import error: {str(e)}")

st.write("---")
st.write("If you see this, the basic app is working!")

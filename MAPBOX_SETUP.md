# 🗺️ Mapbox Setup Guide for CarbonSiteAI

## 🚀 **Get Your Free Mapbox API Key**

### **Step 1: Create Mapbox Account**
1. Go to [Mapbox.com](https://www.mapbox.com/)
2. Click "Sign Up" and create a free account
3. Verify your email address

### **Step 2: Get Your Access Token**
1. Log into your Mapbox account
2. Go to [Account → Access Tokens](https://account.mapbox.com/access-tokens/)
3. Copy your **Default public token** (starts with `pk.`)

### **Step 3: Configure CarbonSiteAI**
1. Copy your token to your `.env` file:
   ```env
   MAPBOX_ACCESS_TOKEN="pk.your_actual_token_here"
   ```

## 🎯 **What You Get with Mapbox**

### **Enhanced Maps**
- **Beautiful industrial maps** with custom styling
- **Interactive markers** for sites, CO₂ sources, and off-takers
- **Clustering** for multiple locations
- **Custom colors** matching your CarbonSiteAI theme

### **Map Features**
- **Site markers** (blue) - Your recommended locations
- **CO₂ source markers** (red) - Industrial facilities
- **Off-taker markers** (green) - Potential buyers
- **Interactive popups** with detailed information
- **Zoom and pan** functionality

## 🔧 **Fallback Options**

If you don't have a Mapbox key, CarbonSiteAI will automatically use:
1. **Folium maps** (OpenStreetMap) - Good quality, completely free
2. **Text summaries** - Location information without maps

## 💰 **Pricing (Free Tier)**
- **50,000 map loads per month** - Perfect for hackathons and demos
- **No credit card required** for free tier
- **Upgrade anytime** if you need more

## 🎉 **Ready to Use!**

Once you add your Mapbox token to `.env`, restart your Streamlit app and you'll see:
- Beautiful, interactive maps
- Professional-looking site visualizations
- Enhanced user experience for your hackathon demo

---

**🌍 Your CarbonSiteAI will now have professional-grade maps that will impress hackathon judges!**

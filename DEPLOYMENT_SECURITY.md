# 🔐 CarbonSiteAI EU - Secure Deployment Guide

## 🚨 **IMPORTANT: API Key Security**

### **❌ NEVER Push These Files:**
- `backend/api_keys.yaml` - Contains your actual API keys
- `.env` files - Environment variables with secrets
- Any file with real API keys or passwords

### **✅ Safe to Push:**
- `api_keys_template.yaml` - Template showing structure
- All Python code files
- Configuration files without secrets
- Documentation

---

## 🛡️ **How to Deploy Securely**

### **Step 1: Local Development (Safe)**
Your API keys work locally because they're in `backend/api_keys.yaml` (not tracked by git)

### **Step 2: GitHub Push (Safe)**
- Your actual API keys stay on your local machine
- Only the template and code get pushed
- Your secrets remain private

### **Step 3: Streamlit Cloud Deployment (Secure)**
Set your API keys as **Environment Variables** in the Streamlit Cloud dashboard:

```toml
GROQ_API_KEY = "your_actual_groq_api_key"
GOOGLE_MAPS_API_KEY = "your_actual_google_maps_api_key"
ELECTRICITY_MAPS_TOKEN = "your_actual_electricity_maps_token"
```

---

## 🔑 **Setting API Keys in Streamlit Cloud:**

### **1. Go to App Settings:**
- In Streamlit Cloud dashboard
- Click on your app
- Go to "Settings" → "Secrets"

### **2. Add these variables:**
```toml
GROQ_API_KEY = "your_groq_api_key_here"
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key_here"
ELECTRICITY_MAPS_TOKEN = "your_electricity_maps_token_here"
```

### **3. Save and Redeploy:**
- Click "Save"
- Redeploy your app
- API keys will be available as environment variables

---

## 🚨 **Security Best Practices:**

### **✅ DO:**
- Keep API keys in environment variables
- Use templates for documentation
- Never commit real secrets
- Use `.gitignore` to protect sensitive files

### **❌ DON'T:**
- Hardcode API keys in code
- Commit `api_keys.yaml` files
- Share API keys in public repositories
- Use real keys in documentation

---

## 🌟 **Result:**
- **Secure deployment** with no exposed secrets
- **Full functionality** with proper API access
- **Professional app** accessible worldwide
- **Peace of mind** knowing your keys are safe

---

## 🔧 **Need Help?**
If you encounter issues:
1. Check that API keys are set in Streamlit Cloud
2. Verify the TOML format is correct
3. Make sure your GitHub account is properly connected
4. Use the robust app version for better error handling

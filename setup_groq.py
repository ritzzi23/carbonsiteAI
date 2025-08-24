#!/usr/bin/env python3
"""
Setup script for Groq API integration
Helps configure the GROQ_API_KEY environment variable
"""

import os
import sys

def setup_groq():
    """Setup Groq API key"""
    print("🚀 Setting up Groq API for AI Site Analysis")
    print("=" * 50)
    
    # Check if key already exists
    existing_key = os.getenv('GROQ_API_KEY')
    if existing_key:
        print(f"✅ GROQ_API_KEY already set: {existing_key[:10]}...")
        return True
    
    print("📋 To use the AI Site Analysis feature, you need a Groq API key.")
    print("\n🔑 How to get your Groq API key:")
    print("1. Go to https://console.groq.com/")
    print("2. Sign up or log in")
    print("3. Navigate to API Keys section")
    print("4. Create a new API key")
    print("5. Copy the key")
    
    print("\n💡 Set your API key using one of these methods:")
    print("\nMethod 1 - Export in terminal:")
    print("export GROQ_API_KEY='your_api_key_here'")
    
    print("\nMethod 2 - Add to ~/.zshrc or ~/.bashrc:")
    print("echo 'export GROQ_API_KEY=\"your_api_key_here\"' >> ~/.zshrc")
    print("source ~/.zshrc")
    
    print("\nMethod 3 - Set for current session:")
    print("GROQ_API_KEY='your_api_key_here' streamlit run streamlit_app_eu.py")
    
    print("\n🎯 After setting the key, restart your terminal and run:")
    print("streamlit run streamlit_app_eu.py")
    
    return False

def test_groq_connection():
    """Test Groq API connection"""
    try:
        from groq import Groq
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("❌ GROQ_API_KEY not found")
            return False
        
        client = Groq(api_key=api_key)
        
        # Test with a simple request
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama-3.1-8b-instant",
            max_tokens=10
        )
        
        print("✅ Groq API connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🤖 CarbonSiteAI - Groq API Setup")
    print("=" * 40)
    
    # Check if groq is installed
    try:
        import groq
        print("✅ Groq library installed")
    except ImportError:
        print("❌ Groq library not installed")
        print("Install with: pip install groq")
        sys.exit(1)
    
    # Setup API key
    if setup_groq():
        print("\n🧪 Testing Groq API connection...")
        test_groq_connection()
    
    print("\n🎉 Setup complete!")
    print("Navigate to the '🤖 AI Site Analysis & Break-Even' tab in your Streamlit app")

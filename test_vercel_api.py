#!/usr/bin/env python3
"""
Test script for Vercel API endpoints
This script verifies the API endpoints are working correctly before deploying to Vercel
"""
import json
import requests

# Base URL for testing (use localhost when testing locally)
BASE_URL = "http://localhost:5000"  
# BASE_URL = "https://your-vercel-deployment-url.vercel.app"  # Uncomment when testing deployed version

def test_status_endpoint():
    """Test the /api/status endpoint"""
    print("Testing /api/status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print("✅ Status endpoint test passed")
    except Exception as e:
        print(f"❌ Status endpoint test failed: {str(e)}")
    print()

def test_chat_endpoint():
    """Test the /api/chat endpoint with different whisky questions"""
    test_messages = [
        "What whisky should I try if I like smoky flavors?",
        "Tell me about whisky regions",
        "I'm new to whisky, what should I try?",
        "What's a good gift whisky?"
    ]
    
    print("Testing /api/chat endpoint...")
    for i, message in enumerate(test_messages):
        print(f"Test {i+1}: {message}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": message}
            )
            response.raise_for_status()
            print(f"Status code: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            print("✅ Chat test passed")
        except Exception as e:
            print(f"❌ Chat test failed: {str(e)}")
        print()

def test_debug_endpoint():
    """Test the /_debug endpoint (if available)"""
    print("Testing /_debug endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/_debug")
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        # Limit output of environment variables for security
        data = response.json()
        if "env" in data:
            keys = list(data["env"].keys())
            print(f"Environment variables: {keys}")
            # Remove sensitive data before printing
            data["env"] = {k: "***" for k in keys}
        print(json.dumps(data, indent=2))
        print("✅ Debug endpoint test passed")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("ℹ️ Debug endpoint not found (this is normal in production)")
        else:
            print(f"❌ Debug endpoint test error: {str(e)}")
    except Exception as e:
        print(f"❌ Debug endpoint test failed: {str(e)}")
    print()

if __name__ == "__main__":
    # Run all tests
    print(f"Testing Vercel API endpoints at: {BASE_URL}\n")
    test_status_endpoint()
    test_chat_endpoint()
    test_debug_endpoint()
    print("All tests completed.")
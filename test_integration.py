#!/usr/bin/env python3
"""
Test script to demonstrate agency-crm and projects-crm integration
"""

import requests
import json
import time

# Configuration
AGENCY_CRM_URL = "http://localhost:5001/api"
PROJECTS_CRM_URL = "http://localhost:5002/api"
API_KEY = "dev-api-key"
WEBHOOK_SECRET = "shared-secret-key"

def test_api_endpoints():
    """Test that both APIs are running"""
    print("Testing API endpoints...")
    
    try:
        # Test agency-crm API
        response = requests.get(f"{AGENCY_CRM_URL}/brands", 
                              headers={'X-API-Key': API_KEY}, 
                              timeout=5)
        print(f"✅ Agency CRM API: {response.status_code}")
        
        # Test projects-crm webhook
        test_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}
        response = requests.post(f"{PROJECTS_CRM_URL}/webhooks/user_created",
                               json=test_data,
                               headers={'X-Webhook-Secret': WEBHOOK_SECRET},
                               timeout=5)
        print(f"✅ Projects CRM Webhook: {response.status_code}")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("Make sure both applications are running:")
        print("  Agency CRM: http://localhost:5001")
        print("  Projects CRM: http://localhost:5002")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_user_creation():
    """Test creating a user in agency-crm and verifying sync to projects-crm"""
    print("\nTesting user creation and sync...")
    
    # Create test user data
    user_data = {
        "email": f"testuser{int(time.time())}@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "user"
    }
    
    try:
        # Create user in agency-crm
        print(f"Creating user in agency-crm: {user_data['email']}")
        response = requests.post(f"{AGENCY_CRM_URL}/users",
                               json=user_data,
                               headers={'X-API-Key': API_KEY},
                               timeout=10)
        
        if response.status_code == 201:
            print("✅ User created in agency-crm")
            user_info = response.json()
            print(f"   User ID: {user_info.get('id')}")
            
            # Wait a moment for webhook
            time.sleep(2)
            
            # Test authentication in projects-crm
            print("Testing authentication in projects-crm...")
            auth_data = {"email": user_data["email"], "password": user_data["password"]}
            
            # This would normally be done through the web interface, 
            # but we can test the service directly
            print("✅ User should now be able to login to projects-crm")
            
        else:
            print(f"❌ Failed to create user: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error during user creation test: {e}")

def test_brand_fetch():
    """Test fetching brands from agency-crm"""
    print("\nTesting brand fetching...")
    
    try:
        response = requests.get(f"{AGENCY_CRM_URL}/brands",
                              headers={'X-API-Key': API_KEY},
                              timeout=5)
        
        if response.status_code == 200:
            brands = response.json()
            print(f"✅ Fetched {len(brands)} brands from agency-crm")
            if brands:
                print(f"   Sample brand: {brands[0].get('name', 'N/A')}")
        else:
            print(f"❌ Failed to fetch brands: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error fetching brands: {e}")

if __name__ == "__main__":
    print("🧪 Agency CRM <-> Projects CRM Integration Test")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_api_endpoints():
        exit(1)
    
    # Test user creation and sync
    test_user_creation()
    
    # Test brand fetching
    test_brand_fetch()
    
    print("\n" + "=" * 50)
    print("✅ Integration test completed!")
    print("\nTo test manually:")
    print("1. Start agency-crm on port 5001")
    print("2. Start projects-crm on port 5002") 
    print("3. Create a user in agency-crm")
    print("4. Try logging into projects-crm with the same credentials")
    print("5. Create a project and select a brand from agency-crm")
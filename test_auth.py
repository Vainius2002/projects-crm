#!/usr/bin/env python3
"""Test projects-crm authentication flow"""

from app import create_app
from app.services import AgencyCRMService

app = create_app()

with app.app_context():
    print("Testing Projects-CRM Authentication")
    print("="*50)
    
    # Check configuration
    print(f"AGENCY_CRM_API_URL: {app.config.get('AGENCY_CRM_API_URL')}")
    print(f"AGENCY_CRM_API_KEY: {app.config.get('AGENCY_CRM_API_KEY')}")
    
    print("\nTesting authentication...")
    
    # Test authentication
    email = "vainius.lunys123@gmail.com"
    password = "password123"
    
    user = AgencyCRMService.authenticate_user(email, password)
    
    if user:
        print(f"✓ Authentication successful!")
        print(f"  User ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Agency CRM ID: {user.agency_crm_id}")
    else:
        print(f"✗ Authentication failed")
        print("\nTrying to get more details...")
        
        # Try a direct API call to see the error
        import requests
        url = f"{app.config['AGENCY_CRM_API_URL']}/auth/login"
        headers = {'X-API-Key': app.config['AGENCY_CRM_API_KEY']}
        data = {'email': email, 'password': password}
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            print(f"API Response Status: {response.status_code}")
            print(f"API Response: {response.text}")
        except Exception as e:
            print(f"API Error: {e}")
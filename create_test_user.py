#!/usr/bin/env python3
"""
Script to create a test user in agency-crm for testing projects-crm login
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../agency-crm'))

from agency_crm_app import create_app, db
from agency_crm_app.models import User

def create_test_user():
    """Create a test user in agency-crm"""
    
    app = create_app()
    
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(email='test@example.com').first()
        
        if existing_user:
            print("✅ Test user already exists!")
            print(f"   Email: {existing_user.email}")
            print(f"   Name: {existing_user.first_name} {existing_user.last_name}")
            print("   Password: testpassword123")
            return
        
        # Create new test user
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='admin',
            is_active=True
        )
        user.set_password('testpassword123')
        
        db.session.add(user)
        db.session.commit()
        
        print("✅ Test user created successfully!")
        print("   Email: test@example.com")
        print("   Password: testpassword123")
        print("   Name: Test User")
        print("   Role: admin")
        print("\nYou can now login to projects-crm with these credentials.")

if __name__ == '__main__':
    try:
        create_test_user()
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        print("Make sure agency-crm database exists and is accessible.")
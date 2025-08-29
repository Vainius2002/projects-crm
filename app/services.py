import requests
from flask import current_app
from app.models import User
from app import db

class AgencyCRMService:
    @staticmethod
    def get_brands():
        """Get all brands from agency-crm API"""
        try:
            url = f"{current_app.config['AGENCY_CRM_API_URL']}/brands"
            headers = {'X-API-Key': current_app.config['AGENCY_CRM_API_KEY']}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            current_app.logger.error(f"Error fetching brands: {str(e)}")
            return []
    
    @staticmethod
    def get_brand(brand_id):
        """Get specific brand from agency-crm API"""
        try:
            url = f"{current_app.config['AGENCY_CRM_API_URL']}/brands/{brand_id}"
            headers = {'X-API-Key': current_app.config['AGENCY_CRM_API_KEY']}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            current_app.logger.error(f"Error fetching brand {brand_id}: {str(e)}")
            return None
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user via agency-crm API and sync user data"""
        try:
            url = f"{current_app.config['AGENCY_CRM_API_URL']}/auth/login"
            headers = {'X-API-Key': current_app.config['AGENCY_CRM_API_KEY']}
            data = {'email': email, 'password': password}
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('success') and 'user' in response_data:
                    user_data = response_data['user']
                    
                    # Find or create user in projects-crm
                    user = User.query.filter_by(email=email).first()
                    if not user:
                        user = User(
                            email=email,
                            first_name=user_data.get('first_name', ''),
                            last_name=user_data.get('last_name', ''),
                            agency_crm_id=user_data.get('id'),
                            is_active=True
                        )
                        db.session.add(user)
                        current_app.logger.info(f"Created new user from agency-crm: {email}")
                    else:
                        # Update existing user data
                        user.first_name = user_data.get('first_name', user.first_name)
                        user.last_name = user_data.get('last_name', user.last_name)
                        user.agency_crm_id = user_data.get('id', user.agency_crm_id)
                        user.is_active = True
                        current_app.logger.info(f"Updated existing user from agency-crm: {email}")
                    
                    db.session.commit()
                    return user
                else:
                    current_app.logger.warning(f"Invalid response format from agency-crm for user: {email}")
                    return None
            elif response.status_code == 401:
                current_app.logger.warning(f"Authentication failed for user: {email}")
                return None
            else:
                current_app.logger.error(f"Agency CRM API error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Network error connecting to agency-crm: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    @staticmethod
    def get_users():
        """Get all users from agency-crm API"""
        try:
            url = f"{current_app.config['AGENCY_CRM_API_URL']}/users"
            headers = {'X-API-Key': current_app.config['AGENCY_CRM_API_KEY']}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            current_app.logger.error(f"Error fetching users: {str(e)}")
            return []
    
    @staticmethod
    def sync_all_users():
        """Sync all users from agency-crm to projects-crm"""
        try:
            users_data = AgencyCRMService.get_users()
            synced_count = 0
            
            for user_data in users_data:
                email = user_data.get('email')
                if not email:
                    continue
                
                user = User.query.filter_by(email=email).first()
                if not user:
                    user = User(
                        email=email,
                        first_name=user_data.get('first_name', ''),
                        last_name=user_data.get('last_name', ''),
                        agency_crm_id=user_data.get('id'),
                        is_active=True
                    )
                    db.session.add(user)
                    synced_count += 1
                else:
                    # Update existing user
                    user.first_name = user_data.get('first_name', user.first_name)
                    user.last_name = user_data.get('last_name', user.last_name)
                    user.agency_crm_id = user_data.get('id', user.agency_crm_id)
            
            db.session.commit()
            current_app.logger.info(f"Synced {synced_count} users from agency-crm")
            return synced_count
        except Exception as e:
            current_app.logger.error(f"Error syncing users: {str(e)}")
            return 0
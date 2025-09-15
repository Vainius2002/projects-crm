import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'projects.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Agency CRM API configuration
    AGENCY_CRM_API_URL = os.environ.get('AGENCY_CRM_API_URL', 'http://localhost:5001/api')
    AGENCY_CRM_API_KEY = os.environ.get('AGENCY_CRM_API_KEY', '')

    # API Configuration
    API_KEY = os.environ.get('API_KEY', 'projects-crm-api-key')
    AGENCY_CRM_URL = os.environ.get('AGENCY_CRM_URL', 'http://localhost:5001')
    AGENCY_CRM_API_KEY = os.environ.get('AGENCY_CRM_API_KEY', 'dev-api-key-change-in-production')
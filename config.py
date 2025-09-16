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
    AGENCY_CRM_API_URL = os.environ.get('AGENCY_CRM_API_URL', 'http://91.99.165.20:5001/api')
    AGENCY_CRM_API_KEY = os.environ.get('AGENCY_CRM_API_KEY', 'my-agency-crm-api-key-change-in-production')

    # API Configuration
    API_KEY = os.environ.get('API_KEY', 'projects-crm-api-key-change-in-production')
    AGENCY_CRM_URL = os.environ.get('AGENCY_CRM_URL', 'http://91.99.165.20:5001')
    AGENCY_CRM_API_KEY = os.environ.get('AGENCY_CRM_API_KEY', 'my-agency-crm-api-key-change-in-production')
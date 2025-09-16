from flask import request, jsonify, current_app
from flask_login import login_user
from app.api import bp
from app.models import User, Project, Campaign, Plan
from app import db
from functools import wraps
import requests
from werkzeug.security import check_password_hash

def require_webhook_secret(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        webhook_secret = request.headers.get('X-Webhook-Secret')
        if not webhook_secret or webhook_secret != 'shared-secret-key':
            return jsonify({'error': 'Invalid webhook secret'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = current_app.config.get('API_KEY', 'projects-api-key')
        if not api_key or api_key != expected_key:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/sync-user', methods=['POST'])
@require_api_key
def sync_user():
    """Sync a user from my-agency-crm"""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'agency_crm_id' not in data:
            return jsonify({'error': 'Email and agency_crm_id required'}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(agency_crm_id=data['agency_crm_id']).first()
        if existing_user:
            # Update existing user
            existing_user.email = data['email']
            existing_user.first_name = data.get('name', '').split(' ')[0] if data.get('name') else ''
            existing_user.last_name = ' '.join(data.get('name', '').split(' ')[1:]) if data.get('name') and len(data.get('name', '').split(' ')) > 1 else ''
            if 'password_hash' in data:
                existing_user.password_hash = data['password_hash']
            db.session.commit()
            return jsonify({'message': 'User updated successfully', 'user_id': existing_user.id}), 200

        # Create new user
        user = User(
            email=data['email'],
            agency_crm_id=data['agency_crm_id'],
            first_name=data.get('name', '').split(' ')[0] if data.get('name') else '',
            last_name=' '.join(data.get('name', '').split(' ')[1:]) if data.get('name') and len(data.get('name', '').split(' ')) > 1 else '',
            password_hash=data.get('password_hash', ''),
            is_active=True
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created successfully', 'user_id': user.id}), 201

    except Exception as e:
        current_app.logger.error(f'Error syncing user: {str(e)}')
        return jsonify({'error': str(e)}), 500

@bp.route('/auth/login-with-agency-crm', methods=['POST'])
def login_with_agency_crm():
    """Authenticate user using my-agency-crm credentials"""
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400

        # First, verify credentials with my-agency-crm
        agency_crm_url = current_app.config.get('AGENCY_CRM_URL', 'http://localhost:5000')
        agency_crm_api_key = current_app.config.get('AGENCY_CRM_API_KEY', 'dev-api-key-change-in-production')

        headers = {
            'X-API-Key': agency_crm_api_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f'{agency_crm_url}/api/authenticate',
            json={'email': data['email'], 'password': data['password']},
            headers=headers,
            timeout=5
        )

        if response.status_code != 200:
            return jsonify({'error': 'Invalid credentials'}), 401

        agency_user = response.json().get('user')

        # Find or create local user
        user = User.query.filter_by(agency_crm_id=agency_user['id']).first()
        if not user:
            # Create user locally
            user = User(
                email=agency_user['email'],
                agency_crm_id=agency_user['id'],
                first_name=agency_user.get('name', '').split(' ')[0] if agency_user.get('name') else '',
                last_name=' '.join(agency_user.get('name', '').split(' ')[1:]) if agency_user.get('name') and len(agency_user.get('name', '').split(' ')) > 1 else '',
                is_active=True
            )
            # Don't set password_hash since we're authenticating via API
            db.session.add(user)
            db.session.commit()

        # Log the user in to projects-crm
        login_user(user)

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 200

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Error connecting to agency-crm: {str(e)}')
        return jsonify({'error': 'Unable to verify credentials'}), 503
    except Exception as e:
        current_app.logger.error(f'Error during authentication: {str(e)}')
        return jsonify({'error': 'Authentication failed'}), 500

@bp.route('/webhooks/user_created', methods=['POST'])
@require_webhook_secret
def webhook_user_created():
    """Webhook endpoint to receive new user notifications from agency-crm"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Invalid data'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            # Update existing user with new data
            existing_user.first_name = data.get('first_name', existing_user.first_name)
            existing_user.last_name = data.get('last_name', existing_user.last_name)
            existing_user.agency_crm_id = data.get('id', existing_user.agency_crm_id)
            db.session.commit()
            return jsonify({'message': 'User updated successfully'}), 200
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            agency_crm_id=data.get('id')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/webhooks/user_updated', methods=['POST'])
@require_webhook_secret
def webhook_user_updated():
    """Webhook endpoint to receive user update notifications from agency-crm"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Invalid data'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            # User doesn't exist, create them
            return webhook_user_created()
        
        # Update user data
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.agency_crm_id = data.get('id', user.agency_crm_id)
        user.is_active = data.get('is_active', user.is_active)
        
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/webhooks/user_deleted', methods=['POST'])
@require_webhook_secret
def webhook_user_deleted():
    """Webhook endpoint to receive user deletion notifications from agency-crm"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Invalid data'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        if user:
            user.is_active = False  # Soft delete - don't delete projects
            db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/campaigns', methods=['GET'])
@require_api_key
def get_campaigns():
    """Get all active campaigns"""
    try:
        campaigns = Campaign.query.join(Project).filter(
            Campaign.status == 'active'
        ).all()
        
        campaign_list = []
        for campaign in campaigns:
            campaign_list.append({
                'id': campaign.id,
                'code': campaign.code,
                'name': campaign.name,
                'project_id': campaign.project_id,
                'project_name': campaign.project.name,
                'project_code': campaign.project.code,
                'client_brand_id': campaign.project.client_brand_id,
                'client_brand_name': campaign.project.client_brand_name,
                'start_date': campaign.start_date.isoformat(),
                'end_date': campaign.end_date.isoformat(),
                'overall_info': campaign.overall_info,
                'status': campaign.status,
                'created_at': campaign.created_at.isoformat()
            })
        
        return jsonify(campaign_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/campaigns/<int:campaign_id>', methods=['GET'])
@require_api_key
def get_campaign(campaign_id):
    """Get specific campaign by ID"""
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        
        campaign_data = {
            'id': campaign.id,
            'code': campaign.code,
            'name': campaign.name,
            'project_id': campaign.project_id,
            'project_name': campaign.project.name,
            'project_code': campaign.project.code,
            'client_brand_id': campaign.project.client_brand_id,
            'client_brand_name': campaign.project.client_brand_name,
            'start_date': campaign.start_date.isoformat(),
            'end_date': campaign.end_date.isoformat(),
            'overall_info': campaign.overall_info,
            'status': campaign.status,
            'created_at': campaign.created_at.isoformat(),
            'updated_at': campaign.updated_at.isoformat()
        }
        
        return jsonify(campaign_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/projects', methods=['GET'])
@require_api_key
def get_projects():
    """Get all active projects"""
    try:
        projects = Project.query.filter(Project.status == 'active').all()
        
        project_list = []
        for project in projects:
            project_list.append({
                'id': project.id,
                'code': project.code,
                'name': project.name,
                'client_brand_id': project.client_brand_id,
                'client_brand_name': project.client_brand_name,
                'start_date': project.start_date.isoformat(),
                'end_date': project.end_date.isoformat(),
                'status': project.status,
                'created_at': project.created_at.isoformat(),
                'campaign_count': len(project.campaigns)
            })
        
        return jsonify(project_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/campaigns/<int:campaign_id>/plans', methods=['GET'])
@require_api_key
def get_campaign_plans(campaign_id):
    """Get all plans for a specific campaign"""
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        
        plans = Plan.query.filter_by(campaign_id=campaign_id).order_by(Plan.created_at.asc()).all()
        
        plan_list = []
        for plan in plans:
            plan_list.append({
                'id': plan.id,
                'name': plan.name,
                'campaign_id': plan.campaign_id,
                'description': plan.description,
                'budget': plan.budget,
                'status': plan.status,
                'created_at': plan.created_at.isoformat(),
                'updated_at': plan.updated_at.isoformat()
            })
        
        return jsonify(plan_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/campaigns/<int:campaign_id>/plans', methods=['POST'])
@require_api_key
def create_plan(campaign_id):
    """Create a new plan for a campaign"""
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get the next plan number for this campaign
        existing_plans = Plan.query.filter_by(campaign_id=campaign_id).count()
        plan_number = existing_plans + 1
        
        # Create plan name if not provided
        plan_name = data.get('name') or f'Plan{plan_number}'
        
        # Create the plan
        plan = Plan(
            name=plan_name,
            campaign_id=campaign_id,
            description=data.get('description', ''),
            budget=data.get('budget', 0.0),
            status=data.get('status', 'draft')
        )
        
        db.session.add(plan)
        db.session.commit()
        
        plan_data = {
            'id': plan.id,
            'name': plan.name,
            'campaign_id': plan.campaign_id,
            'description': plan.description,
            'budget': plan.budget,
            'status': plan.status,
            'created_at': plan.created_at.isoformat(),
            'updated_at': plan.updated_at.isoformat()
        }
        
        return jsonify(plan_data), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/plans/<int:plan_id>', methods=['GET'])
@require_api_key
def get_plan(plan_id):
    """Get specific plan by ID"""
    try:
        plan = Plan.query.get_or_404(plan_id)
        
        plan_data = {
            'id': plan.id,
            'name': plan.name,
            'campaign_id': plan.campaign_id,
            'campaign_name': plan.campaign.name,
            'campaign_code': plan.campaign.code,
            'description': plan.description,
            'budget': plan.budget,
            'status': plan.status,
            'created_at': plan.created_at.isoformat(),
            'updated_at': plan.updated_at.isoformat()
        }
        
        return jsonify(plan_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/campaigns/sync-to-ekranu', methods=['POST'])
@require_api_key
def sync_campaigns_to_ekranu():
    """Send active campaigns to ekranu-crm as kampanijos"""
    try:
        # Get all active campaigns with their projects
        campaigns = Campaign.query.join(Project).filter(
            Campaign.status == 'active'
        ).all()
        
        # Prepare data for ekranu-crm kampanijos
        campaigns_data = []
        for campaign in campaigns:
            campaigns_data.append({
                'name': f"{campaign.project.client_brand_name} - {campaign.name}",  # Brand + Campaign name
                'client_brand_name': campaign.project.client_brand_name,
                'campaign_name': campaign.name,
                'external_id': f'projects_campaign_{campaign.id}',  # Unique identifier
                'source_system': 'projects-crm'
            })
        
        # Send to ekranu-crm kampanijos endpoint using localhost
        ekranu_url = 'http://localhost:5003/api/import-kampanijos'
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'ekranu-crm-api-key'  # This should match the key in ekranu-crm
        }
        
        response = requests.post(ekranu_url, json={'kampanijos': campaigns_data}, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'message': f'Successfully synced {len(campaigns_data)} campaigns to ekranu-crm',
                'synced_count': result.get('imported_count', len(campaigns_data))
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to sync campaigns: {response.text}'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'Connection error to ekranu-crm: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error syncing campaigns: {str(e)}'
        }), 500

@bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@require_api_key
def delete_plan(plan_id):
    """Delete a plan"""
    try:
        plan = Plan.query.get_or_404(plan_id)
        
        # Store plan info for response
        plan_info = {
            'id': plan.id,
            'name': plan.name,
            'campaign_id': plan.campaign_id
        }
        
        # Delete the plan
        db.session.delete(plan)
        db.session.commit()
        
        return jsonify({
            'message': f'Plan "{plan_info["name"]}" deleted successfully',
            'deleted_plan': plan_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/campaigns/<int:campaign_id>/plans/by-name/<plan_name>', methods=['DELETE'])
@require_api_key
def delete_plan_by_name(campaign_id, plan_name):
    """Delete a plan by name (useful for TV-Planner sync)"""
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        
        # Find the plan by name in this campaign
        plan = Plan.query.filter_by(
            campaign_id=campaign_id, 
            name=plan_name
        ).first()
        
        if not plan:
            return jsonify({'error': f'Plan "{plan_name}" not found in campaign'}), 404
        
        # Store plan info for response
        plan_info = {
            'id': plan.id,
            'name': plan.name,
            'campaign_id': plan.campaign_id
        }
        
        # Delete the plan
        db.session.delete(plan)
        db.session.commit()
        
        return jsonify({
            'message': f'Plan "{plan_name}" deleted successfully',
            'deleted_plan': plan_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/plans/<int:plan_id>', methods=['PATCH'])
@require_api_key
def update_plan(plan_id):
    """Update a plan"""
    try:
        plan = Plan.query.get_or_404(plan_id)
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            plan.name = data['name']
        if 'description' in data:
            plan.description = data['description']
        if 'budget' in data:
            plan.budget = float(data['budget'])
        if 'status' in data:
            plan.status = data['status']
        
        db.session.commit()
        
        plan_data = {
            'id': plan.id,
            'name': plan.name,
            'campaign_id': plan.campaign_id,
            'description': plan.description,
            'budget': plan.budget,
            'status': plan.status,
            'created_at': plan.created_at.isoformat(),
            'updated_at': plan.updated_at.isoformat()
        }
        
        return jsonify(plan_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
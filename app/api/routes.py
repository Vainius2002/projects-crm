from flask import request, jsonify
from app.api import bp
from app.models import User, Project, Campaign
from app import db
from functools import wraps

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
        if not api_key or api_key != 'projects-api-key':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

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
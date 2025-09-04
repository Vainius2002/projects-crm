from flask import jsonify
from app.api import bp
from app.models import Campaign, Project
from app.api.routes import require_api_key

@bp.route('/campaigns/for-ekranu', methods=['GET'])
@require_api_key
def get_campaigns_for_ekranu():
    """Get active campaigns formatted for ekranu-crm selection"""
    try:
        campaigns = Campaign.query.join(Project).filter(
            Campaign.status == 'active'
        ).all()
        
        campaign_list = []
        for campaign in campaigns:
            campaign_list.append({
                'id': campaign.id,
                'name': f"{campaign.project.client_brand_name} - {campaign.name}",
                'client_brand_name': campaign.project.client_brand_name,
                'campaign_name': campaign.name,
                'project_code': campaign.project.code,
                'campaign_code': campaign.code,
                'start_date': campaign.start_date.isoformat(),
                'end_date': campaign.end_date.isoformat(),
                'external_id': f'projects_campaign_{campaign.id}',
                'source_system': 'projects-crm'
            })
        
        return jsonify(campaign_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
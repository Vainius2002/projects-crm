from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.main import bp
from app.models import Project, Campaign

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        recent_projects = Project.query.filter_by(created_by=current_user).order_by(Project.created_at.desc()).limit(5).all()
        total_projects = Project.query.filter_by(created_by=current_user).count()
        total_campaigns = Campaign.query.join(Project).filter(Project.created_by == current_user).count()
        
        return render_template('main/index.html', 
                             title='Dashboard',
                             recent_projects=recent_projects,
                             total_projects=total_projects,
                             total_campaigns=total_campaigns)
    return redirect(url_for('auth.login'))
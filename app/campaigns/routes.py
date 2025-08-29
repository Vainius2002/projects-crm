from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.campaigns import bp
from app.campaigns.forms import CampaignForm, PlanForm
from app.models import Project, Campaign, Plan
from app import db

@bp.route('/project/<int:project_id>')
@login_required
def index(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('campaigns/index.html', title='Campaigns', project=project)

@bp.route('/project/<int:project_id>/create', methods=['GET', 'POST'])
@login_required
def create(project_id):
    project = Project.query.get_or_404(project_id)
    if project.created_by != current_user:
        flash('You do not have permission to add campaigns to this project.', 'danger')
        return redirect(url_for('projects.view', id=project_id))
    
    form = CampaignForm()
    
    if form.validate_on_submit():
        campaign = Campaign(
            code=Campaign.generate_campaign_code(project.code),
            name=form.name.data,
            project=project,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            overall_info=form.overall_info.data
        )
        db.session.add(campaign)
        db.session.commit()
        flash(f'Campaign {campaign.code} created successfully!', 'success')
        return redirect(url_for('campaigns.view', id=campaign.id))
    
    return render_template('campaigns/form.html', title='Create Campaign', form=form, project=project)

@bp.route('/<int:id>')
@login_required
def view(id):
    campaign = Campaign.query.get_or_404(id)
    return render_template('campaigns/view.html', title=campaign.name, campaign=campaign)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    campaign = Campaign.query.get_or_404(id)
    if campaign.project.created_by != current_user:
        flash('You do not have permission to edit this campaign.', 'danger')
        return redirect(url_for('campaigns.view', id=id))
    
    form = CampaignForm(obj=campaign)
    
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.overall_info = form.overall_info.data
        db.session.commit()
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('campaigns.view', id=campaign.id))
    
    return render_template('campaigns/form.html', title='Edit Campaign', form=form, campaign=campaign)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    campaign = Campaign.query.get_or_404(id)
    project_id = campaign.project_id
    if campaign.project.created_by != current_user:
        flash('You do not have permission to delete this campaign.', 'danger')
        return redirect(url_for('projects.view', id=project_id))
    
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('projects.view', id=project_id))

@bp.route('/<int:campaign_id>/plans/create', methods=['GET', 'POST'])
@login_required
def create_plan(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.project.created_by != current_user:
        flash('You do not have permission to add plans to this campaign.', 'danger')
        return redirect(url_for('campaigns.view', id=campaign_id))
    
    form = PlanForm()
    
    if form.validate_on_submit():
        plan = Plan(
            name=form.name.data,
            campaign=campaign,
            description=form.description.data,
            budget=form.budget.data
        )
        db.session.add(plan)
        db.session.commit()
        flash('Plan created successfully!', 'success')
        return redirect(url_for('campaigns.view', id=campaign_id))
    
    return render_template('campaigns/plan_form.html', title='Create Plan', form=form, campaign=campaign)

@bp.route('/plans/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_plan(id):
    plan = Plan.query.get_or_404(id)
    if plan.campaign.project.created_by != current_user:
        flash('You do not have permission to edit this plan.', 'danger')
        return redirect(url_for('campaigns.view', id=plan.campaign_id))
    
    form = PlanForm(obj=plan)
    
    if form.validate_on_submit():
        plan.name = form.name.data
        plan.description = form.description.data
        plan.budget = form.budget.data
        db.session.commit()
        flash('Plan updated successfully!', 'success')
        return redirect(url_for('campaigns.view', id=plan.campaign_id))
    
    return render_template('campaigns/plan_form.html', title='Edit Plan', form=form, plan=plan)

@bp.route('/plans/<int:id>/delete', methods=['POST'])
@login_required
def delete_plan(id):
    plan = Plan.query.get_or_404(id)
    campaign_id = plan.campaign_id
    if plan.campaign.project.created_by != current_user:
        flash('You do not have permission to delete this plan.', 'danger')
        return redirect(url_for('campaigns.view', id=campaign_id))
    
    db.session.delete(plan)
    db.session.commit()
    flash('Plan deleted successfully!', 'success')
    return redirect(url_for('campaigns.view', id=campaign_id))
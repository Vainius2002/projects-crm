from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.projects import bp
from app.projects.forms import ProjectForm
from app.models import Project, Campaign
from app.services import AgencyCRMService
from app import db

@bp.route('/')
@login_required
def index():
    projects = Project.query.filter_by(created_by=current_user).order_by(Project.created_at.desc()).all()
    return render_template('projects/index.html', title='Projects', projects=projects)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProjectForm()
    
    brands = AgencyCRMService.get_brands()
    form.client_brand_id.choices = [(0, 'Select a brand')] + [(b['id'], b['full_name']) for b in brands]
    
    if form.validate_on_submit():
        project = Project(
            code=Project.generate_project_code(),
            name=form.name.data,
            client_brand_id=form.client_brand_id.data,
            client_brand_name=next((b['full_name'] for b in brands if b['id'] == form.client_brand_id.data), ''),
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            comments=form.comments.data,
            overall_info=form.overall_info.data,
            created_by=current_user
        )
        db.session.add(project)
        db.session.commit()
        flash(f'Project {project.code} created successfully!', 'success')
        return redirect(url_for('projects.view', id=project.id))
    
    return render_template('projects/form.html', title='Create Project', form=form)

@bp.route('/<int:id>')
@login_required
def view(id):
    project = Project.query.get_or_404(id)
    return render_template('projects/view.html', title=project.name, project=project)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    project = Project.query.get_or_404(id)
    if project.created_by != current_user:
        flash('You do not have permission to edit this project.', 'danger')
        return redirect(url_for('projects.index'))
    
    form = ProjectForm(obj=project)
    
    brands = AgencyCRMService.get_brands()
    form.client_brand_id.choices = [(0, 'Select a brand')] + [(b['id'], b['full_name']) for b in brands]
    
    if form.validate_on_submit():
        project.name = form.name.data
        project.client_brand_id = form.client_brand_id.data
        project.client_brand_name = next((b['full_name'] for b in brands if b['id'] == form.client_brand_id.data), '')
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.comments = form.comments.data
        project.overall_info = form.overall_info.data
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects.view', id=project.id))
    
    return render_template('projects/form.html', title='Edit Project', form=form, project=project)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    project = Project.query.get_or_404(id)
    if project.created_by != current_user:
        flash('You do not have permission to delete this project.', 'danger')
        return redirect(url_for('projects.index'))
    
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('projects.index'))
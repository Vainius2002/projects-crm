from app import create_app, db
from app.models import User, Project, Campaign, Plan
from app.services import AgencyCRMService
import click

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Project': Project, 'Campaign': Campaign, 'Plan': Plan}

@app.cli.command()
def sync_users():
    """Sync users from agency-crm to projects-crm"""
    click.echo('Syncing users from agency-crm...')
    synced_count = AgencyCRMService.sync_all_users()
    click.echo(f'Successfully synced {synced_count} users')

@app.cli.command()
def create_db():
    """Create database tables"""
    db.create_all()
    click.echo('Database tables created successfully')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)
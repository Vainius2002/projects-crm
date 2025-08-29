from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager
import string

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    agency_crm_id = db.Column(db.Integer, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    projects = db.relationship('Project', back_populates='created_by', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    client_brand_id = db.Column(db.Integer, nullable=False)
    client_brand_name = db.Column(db.String(200))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    comments = db.Column(db.Text)
    overall_info = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_by = db.relationship('User', back_populates='projects')
    campaigns = db.relationship('Campaign', back_populates='project', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_project_code():
        current_year = datetime.now().year % 100
        
        last_project = Project.query.filter(
            Project.code.like(f'PLN-{current_year:02d}-%')
        ).order_by(Project.id.desc()).first()
        
        if last_project:
            last_number = int(last_project.code.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'PLN-{current_year:02d}-{new_number:03d}'
    
    def __repr__(self):
        return f'<Project {self.code}: {self.name}>'

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(25), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    overall_info = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('Project', back_populates='campaigns')
    plans = db.relationship('Plan', back_populates='campaign', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_campaign_code(project_code):
        last_campaign = Campaign.query.join(Project).filter(
            Project.code == project_code
        ).order_by(Campaign.id.desc()).first()
        
        if last_campaign:
            last_letter = last_campaign.code.split('-')[-1]
            if last_letter and last_letter[0] in string.ascii_uppercase:
                next_index = string.ascii_uppercase.index(last_letter[0]) + 1
                if next_index < len(string.ascii_uppercase):
                    next_letter = string.ascii_uppercase[next_index]
                else:
                    next_letter = 'AA'
            else:
                next_letter = 'A'
        else:
            next_letter = 'A'
        
        return f'{project_code}-{next_letter}'
    
    def __repr__(self):
        return f'<Campaign {self.code}: {self.name}>'

class Plan(db.Model):
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    description = db.Column(db.Text)
    budget = db.Column(db.Float)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    campaign = db.relationship('Campaign', back_populates='plans')
    
    def __repr__(self):
        return f'<Plan {self.name}>'
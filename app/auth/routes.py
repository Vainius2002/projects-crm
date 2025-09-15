from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.models import User
from app.auth.forms import LoginForm
from app import db
import requests

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # First try to authenticate with my-agency-crm
        try:
            agency_crm_url = current_app.config.get('AGENCY_CRM_URL', 'http://localhost:5000')
            agency_crm_api_key = current_app.config.get('AGENCY_CRM_API_KEY', 'dev-api-key-change-in-production')

            headers = {
                'X-API-Key': agency_crm_api_key,
                'Content-Type': 'application/json'
            }

            response = requests.post(
                f'{agency_crm_url}/api/authenticate',
                json={'email': form.email.data, 'password': form.password.data},
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
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
                    db.session.add(user)
                    db.session.commit()

                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))

        except requests.exceptions.RequestException:
            # If agency-crm is not available, fall back to local authentication
            pass

        # Fall back to local authentication
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))

        flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
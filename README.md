# Projects CRM

A project and campaign management system integrated with Agency CRM for user authentication and brand data.

## Features

### Project Management
- ✅ Create projects with unique codes (PLN-YY-XXX format)
- ✅ Select client brands from Agency CRM
- ✅ Set start/end dates, comments, and project info
- ✅ Track project status and statistics

### Campaign Management
- ✅ Add multiple campaigns to projects
- ✅ Unique campaign codes with letter suffixes (PLN-YY-XXX-A, B, C...)
- ✅ Campaign start/end dates and information

### Plan Management
- ✅ Add multiple plans to campaigns
- ✅ Plan descriptions and budget tracking
- ✅ Plan status management

### Agency CRM Integration
- ✅ User authentication via Agency CRM API
- ✅ Automatic user synchronization
- ✅ Brand data fetching from Agency CRM
- ✅ Webhook system for real-time user updates

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Agency CRM running on port 5000
- SQLite (included with Python)

### 2. Installation

```bash
cd /home/vainiusl/py_projects/projects-crm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file (already created):
```bash
SECRET_KEY=dev-secret-key-change-in-production-12345
DATABASE_URL=sqlite:///projects.db
AGENCY_CRM_API_URL=http://localhost:5001/api
AGENCY_CRM_API_KEY=dev-api-key
```

### 4. Database Setup

```bash
# Create database tables
source venv/bin/activate
flask create-db

# Optional: Sync existing users from Agency CRM
flask sync-users
```

### 5. Running the Application

```bash
source venv/bin/activate
python run.py
```

The application will be available at `http://localhost:5002`

## API Integration Details

### Agency CRM API Endpoints

The following endpoints were added to Agency CRM (`/api/`):

- `POST /auth/login` - User authentication
- `GET /users` - Get all users  
- `POST /users` - Create new user (triggers webhook)
- `PUT /users/<id>` - Update user (triggers webhook)
- `GET /brands` - Get all brands
- `GET /brands/<id>` - Get specific brand

### Projects CRM Webhook Endpoints

The following webhook endpoints receive notifications from Agency CRM:

- `POST /api/webhooks/user_created` - New user created
- `POST /api/webhooks/user_updated` - User updated
- `POST /api/webhooks/user_deleted` - User deactivated

### User Synchronization Flow

1. **New User Creation in Agency CRM:**
   - User created in Agency CRM
   - Webhook sent to Projects CRM
   - User automatically created in Projects CRM
   - User can immediately login to Projects CRM

2. **User Login:**
   - User enters credentials in Projects CRM
   - Credentials verified against Agency CRM API
   - User data synced/updated in Projects CRM
   - Login session created

3. **User Updates:**
   - User updated in Agency CRM
   - Webhook sent to Projects CRM
   - User data automatically updated

## Testing

Run the integration test:

```bash
python test_integration.py
```

### Manual Testing Steps

1. **Start both applications:**
   ```bash
   # Terminal 1 - Agency CRM
   cd /home/vainiusl/py_projects/agency-crm
   source venv/bin/activate
   python run.py  # Runs on port 5000
   
   # Terminal 2 - Projects CRM  
   cd /home/vainiusl/py_projects/projects-crm
   source venv/bin/activate
   python run.py  # Runs on port 5002
   ```

2. **Create a test user in Agency CRM:**
   - Go to `http://localhost:5000`
   - Register/create a new user account

3. **Login to Projects CRM:**
   - Go to `http://localhost:5002`
   - Login with the same credentials
   - User should be automatically synced

4. **Create a project:**
   - Click "New Project"
   - Select a brand from the dropdown (fetched from Agency CRM)
   - Fill in project details
   - Verify unique code generation (PLN-YY-XXX)

5. **Add campaigns and plans:**
   - Add campaigns to the project
   - Verify campaign codes (PLN-YY-XXX-A, B, C...)
   - Add plans to campaigns

## Code Structure

```
projects-crm/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── services.py          # Agency CRM API service
│   ├── auth/                # Authentication blueprint
│   ├── projects/            # Projects management blueprint
│   ├── campaigns/           # Campaigns management blueprint
│   ├── main/                # Main dashboard blueprint
│   ├── api/                 # Webhook API blueprint
│   └── templates/           # Jinja2 templates
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Dependencies
├── test_integration.py      # Integration test script
└── README.md               # This file
```

## Security Considerations

- API keys are used for service-to-service communication
- Webhook secrets prevent unauthorized webhook calls
- User sessions are managed securely with Flask-Login
- Passwords are never stored in Projects CRM (authenticated via Agency CRM)

## Troubleshooting

### Common Issues

1. **Connection refused errors:**
   - Ensure Agency CRM is running on port 5000
   - Check `.env` file configuration

2. **User sync not working:**
   - Verify webhook secret matches between applications
   - Check application logs for errors
   - Test with `python test_integration.py`

3. **Brand dropdown empty:**
   - Ensure Agency CRM has active brands
   - Check API key configuration
   - Verify Agency CRM API endpoints are accessible

### Debug Commands

```bash
# Test user sync manually
flask sync-users

# Check database contents
flask shell
>>> User.query.all()
>>> Project.query.all()
```

## Production Deployment

For production deployment:

1. Change `SECRET_KEY` to a secure random value
2. Use a production WSGI server (gunicorn, uwsgi)
3. Use a production database (PostgreSQL, MySQL)
4. Secure API keys and webhook secrets
5. Enable HTTPS
6. Set up proper logging
7. Configure firewall rules for API communication
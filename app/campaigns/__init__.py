from flask import Blueprint

bp = Blueprint('campaigns', __name__)

from app.campaigns import routes
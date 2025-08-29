from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired(), Length(min=1, max=200)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    overall_info = TextAreaField('Overall Information')
    submit = SubmitField('Save Campaign')

class PlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    budget = FloatField('Budget', validators=[Optional()])
    submit = SubmitField('Save Plan')
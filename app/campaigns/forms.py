from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired(), Length(min=1, max=200)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    overall_info = TextAreaField('Overall Information')
    submit = SubmitField('Save Campaign')
    
    def __init__(self, project=None, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        self.project = project
    
    def validate_start_date(self, field):
        if self.project and field.data:
            if field.data < self.project.start_date:
                raise ValidationError(f'Campaign start date cannot be before project start date ({self.project.start_date.strftime("%Y-%m-%d")})')
            if field.data > self.project.end_date:
                raise ValidationError(f'Campaign start date cannot be after project end date ({self.project.end_date.strftime("%Y-%m-%d")})')
    
    def validate_end_date(self, field):
        if self.project and field.data:
            if field.data < self.project.start_date:
                raise ValidationError(f'Campaign end date cannot be before project start date ({self.project.start_date.strftime("%Y-%m-%d")})')
            if field.data > self.project.end_date:
                raise ValidationError(f'Campaign end date cannot be after project end date ({self.project.end_date.strftime("%Y-%m-%d")})')
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError('Campaign end date cannot be before start date')

class PlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    budget = FloatField('Budget', validators=[Optional()])
    submit = SubmitField('Save Plan')
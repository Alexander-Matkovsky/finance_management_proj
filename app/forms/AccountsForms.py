from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AccountForm(FlaskForm):
    account_name = StringField('Account Name', validators=[DataRequired()])
    initial_balance = FloatField('Initial Balance', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Account')

class AccountUpdateForm(FlaskForm):
    account_name = StringField('Account Name', validators=[DataRequired()])
    new_balance = FloatField('New Balance', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Account')
from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, HiddenField, IntegerField, SelectField, StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp, NumberRange
from app.models.database import get_connection, UserOperations

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="Invalid email address.")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        db = get_connection()
        user_ops = UserOperations(db)
        user = user_ops.get_user_by_email(email.data)
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AdminCreationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    admin_secret = PasswordField('Admin Secret', validators=[DataRequired()])
    submit = SubmitField('Create Admin')

class BudgetForm(FlaskForm):
    budget_name = StringField('Budget Name', validators=[DataRequired()])
    initial_amount = FloatField('Initial Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Budget')

class UpdateBudgetForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=100)])
    new_amount = FloatField('New Amount', validators=[DataRequired()])
    submit = SubmitField('Update Budget')

#transactions

class TransactionForm(FlaskForm):
    account_id = IntegerField('Account ID', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    type = SelectField('Type', choices=[('income', 'Income'), ('expense', 'Expense')], validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    category_name = StringField('Category', validators=[DataRequired()])

class TransactionUpdateForm(TransactionForm):
    transaction_id = IntegerField('Transaction ID', validators=[DataRequired()])

class TransactionDeleteForm(FlaskForm):
    confirm = StringField('Type DELETE to confirm', validators=[DataRequired()])

class UpdateUserForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=2, max=100)])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('New Password', validators=[Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('password')])
    submit = SubmitField('Update')
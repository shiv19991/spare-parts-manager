from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Machine

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AddMachineForm(FlaskForm):
    name = StringField('Machine Name', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Add Machine')

class AddPartForm(FlaskForm):
    name = StringField('Part Name', validators=[DataRequired()])
    part_number = StringField('Part Number', validators=[DataRequired()])
    total_received = IntegerField('Initial Quantity', validators=[DataRequired()])
    machine = SelectField('Machine', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Part')

    def __init__(self, *args, **kwargs):
        super(AddPartForm, self).__init__(*args, **kwargs)
        self.machine.choices = [(m.id, m.name) for m in Machine.query.order_by(Machine.name).all()]

class ConsumePartForm(FlaskForm):
    quantity = IntegerField('Quantity to Consume', validators=[DataRequired()])
    notes = StringField('Notes')
    submit = SubmitField('Consume')
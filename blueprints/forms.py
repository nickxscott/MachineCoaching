from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField, DateField, TimeField
from wtforms.validators import InputRequired, Email, Length, EqualTo, NumberRange

from .functions import createList, createSec

class loginForm(FlaskForm):
	email = StringField("email", validators=[InputRequired()],render_kw={"placeholder": "Email Address"}) 
	pwd=PasswordField("pwd", validators=[InputRequired(), Length(min=8, message='Too short')],render_kw={"placeholder": "Password"}) 

class regForm(FlaskForm):
	f_name = StringField("first", validators=[InputRequired(message='Must enter first name')], render_kw={"placeholder": "First Name"})
	l_name = StringField("last", validators=[InputRequired(message='Must enter last name')], render_kw={"placeholder": "Last Name"})
	email = StringField("email", validators=[InputRequired(),Email(	check_deliverability=True, message='Not a valid email address')],
						render_kw={"placeholder": "Email Address"}) 
	pwd=PasswordField(	"pwd", 
						validators=[InputRequired(), 
									Length(	min=8, message='Too short')], 
						render_kw={"placeholder": "Password"}) 
	confirm_pwd = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('pwd', message='Passwords must match')],
								render_kw={"placeholder": "Confirm password"})
	terms = BooleanField("terms", validators=[InputRequired(message='must agree to terms of service')])

class planForm(FlaskForm):
	date = DateField("date", validators=[InputRequired(message='Must enter a race date')])
	dist = SelectField("distance", validators=[InputRequired(message='Must enter a race distance')],
						choices=[(3.1, '5k'), (6.2, '10k'), (13.1, 'Half-Marathon'), (26.2, 'Marathon')])
	weeks=SelectField("weeks", validators=[InputRequired()],
						choices=createList(8,16), default=12)
	#pace = TimeField('pace', validators=[InputRequired()])
	pace_min=SelectField("pace_min", validators=[InputRequired(message='Must enter a pace')],
							choices=createList(3,12), default=8) 
	pace_sec = SelectField("pace_sec", validators=[InputRequired(message='Must enter a pace')],
							choices=createSec(0,59))
	units = SelectField("units", validators=[InputRequired(message='Must enter a distance unit')],
						choices=['mile', 'km'])
	name = StringField("name", validators=[InputRequired()], render_kw={"placeholder": "Example: NYC Marathon"})
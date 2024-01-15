from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField, SelectMultipleField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo

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

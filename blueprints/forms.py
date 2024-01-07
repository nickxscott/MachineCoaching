from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField, SelectMultipleField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class loginForm(FlaskForm):
	email = StringField("email", validators=[InputRequired()],render_kw={"placeholder": "Email Address"}) 
	pwd=PasswordField("pwd", validators=[InputRequired(), Length(min=8, message='Too short')],render_kw={"placeholder": "Password"}) 

class regForm(FlaskForm):
	f_name = StringField("first", validators=[InputRequired()])
	l_name = StringField("last", validators=[InputRequired()])
	email = StringField("email", validators=[	InputRequired(), 
												Email(	check_deliverability=True, 
														message='Not a valid email address')],
								render_kw={"placeholder": "Email Address"}) 
	pwd=PasswordField(	"pwd", 
						validators=[InputRequired(), 
									Length(	min=8, 
											message='Too short')], 
						render_kw={"placeholder": "Password"}) 
	confirm_pwd = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('pwd', message='Both password fields must be equal!')])

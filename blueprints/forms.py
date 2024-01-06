from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField, SelectMultipleField, BooleanField
from wtforms.validators import InputRequired, Email

class loginForm(FlaskForm):
	email = StringField("email", validators=[InputRequired()],render_kw={"placeholder": "Email Address"}) 
	pwd=PasswordField("pwd", validators=[InputRequired()],render_kw={"placeholder": "Password"}) 

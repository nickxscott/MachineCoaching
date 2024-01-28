
#flask imports
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user



#custom imports
from ..forms import *
from ..functions import *
from ..user import User
from app import bcrypt, login_manager


login_bp = Blueprint('login', __name__, template_folder='../templates')




@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_bp.route('/', methods=['GET','POST'])
def login():

	form = loginForm()
	#user = form.email.data
	#pw = form.pwd.data

	if request.method=='POST' and form.validate_on_submit():
		user = form.email.data
		pw = form.pwd.data
		#hashed_password = bcrypt.generate_password_hash(pw).decode('utf-8')
		if check_user(username=user):	
			#fetch user credentials from USER table in db
			df_user=get_user(username=user)
			hashed_password=df_user.pwd.values[0]
	
			if bcrypt.check_password_hash(hashed_password, pw):
				#unique_id = userinfo_response["sub"]
				#user_email = userinfo_response["email"]
				#user_name = userinfo_response["name"]
				#user = User(user_id, first, last, email)
				user=User(	user_id=df_user.user_id.values[0], 
							first=df_user.first_name.values[0], 
							last=df_user.last_name.values[0], 
							email=df_user.email.values[0])
				login_user(user)
				return redirect(url_for('dashboard.dashboard'))
			else:
				flash('Incorrect username or password')
				return render_template('/login/login.html', form=form, error=True)
		else:
			flash('No user account exists with this email address. Create account an account using the link below')
			return render_template('/login/login.html', form=form, error=True)

	else:
		for fieldName, errorMessages in form.errors.items():
			for err in errorMessages:
				flash(err )
		return render_template('/login/login.html', form=form)

@login_bp.route('/register', methods=['GET','POST'])
def reg():
	form = regForm()

	if request.method=='GET':
		return render_template('/login/register.html', form=form, error=False)

	elif request.method=='POST' and form.validate_on_submit():

		last = form.l_name.data
		first = form.f_name.data
		email = form.email.data
		pwd = form.pwd.data
		terms = form.terms.data
		hashed_pwd = bcrypt.generate_password_hash(pwd).decode('utf-8')

		#check_user function returns boolean value to indicate if email already exist in db or not
		if check_user(username=email):
			flash('Username exists already. Return to login page')
			return render_template('/login/register.html', form=form, error=True)
		else:
			new_user(first=first, last=last, email=email, hashed_pwd=hashed_pwd)
			return render_template('/login/success.html')

	else:
		for fieldName, errorMessages in form.errors.items():
			for err in errorMessages:
				flash(err )
		return render_template('/login/register.html', form=form, error=True)


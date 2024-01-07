
#imports
from flask import Blueprint, render_template, request, flash
from flask_login import login_user, login_required, logout_user, current_user

#custom imports
from ..forms import *
from app import bcrypt, login_manager


login_bp = Blueprint('login', __name__, template_folder='../templates')


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_bp.route('/', methods=['GET','POST'])
def login():

	form = loginForm()
	user = form.email.data
	pw = form.pwd.data

	if request.method=='POST' and form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(pw).decode('utf-8')
		flash(user)
		flash(pw)
		flash(hashed_password)
		if bcrypt.check_password_hash('$2b$12$bM5kzsMl5CsL0Yr4eB.Dm.jrXKk59ByG0vwAOtgSAa9yk7hIggPky', pw):
			flash('hashing worked')

		else:
			flash('it didnt work')
		return render_template('/login/login.html', form=form)

	else:
		for fieldName, errorMessages in form.errors.items():
			for err in errorMessages:
				flash(err )
		return render_template('/login/login.html', form=form)

@login_bp.route('/register')
def reg():
	return render_template('/login/register.html')
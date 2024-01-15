
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
	#user = form.email.data
	#pw = form.pwd.data

	if request.method=='POST' and form.validate_on_submit():
		user = form.email.data
		pw = form.pwd.data
		hashed_password = bcrypt.generate_password_hash(pw).decode('utf-8')
		flash(user)
		flash(pw)
		flash(hashed_password)
		return render_template('/login/login.html', form=form)

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
		flash('success')
		last = form.l_name.data
		first = form.f_name.data
		email = form.email.data
		pwd = form.pwd.data
		terms = form.terms.data
		flash(first)
		flash(last)
		flash(email)
		flash(pwd)

		return render_template('/login/register.html', form=form, error=False)

	else:
		for fieldName, errorMessages in form.errors.items():
			for err in errorMessages:
				flash(err )
		return render_template('/login/register.html', form=form, error=True)

@login_bp.route('/test', methods=['GET','POST'])
def test():
	return render_template('/login/test.html')
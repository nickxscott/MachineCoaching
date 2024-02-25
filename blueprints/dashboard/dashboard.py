
#flask imports
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, logout_user, current_user



#custom imports
from ..forms import *
from ..functions import *
from ..user import User
from app import bcrypt, login_manager


dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@login_manager.user_loader
def load_user(user_id):
	return User.get(user_id)

@dashboard_bp.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
	user=current_user
	#if request.method=='GET':
		
	return render_template('/dashboard/dashboard.html', user=user)

@dashboard_bp.route('/create', methods=['GET','POST'])
@login_required
def create():

	form = planForm()
	user=current_user

	if request.method=='GET':

		return render_template('/dashboard/create.html', user=user, form=form)

	elif request.method=='POST':

		race_name=form.name.data
		race_date=form.date.data
		weeks=int(form.weeks.data)

		return render_template('/dashboard/planSubmit.html', 
								user=user, 
								race=race_name,
								date=race_date)

@dashboard_bp.route('/logout', methods=['GET','POST'])
@login_required
def logout():
	logout_user()
	#flash('You have successfully logged yourself out.')
	return redirect(url_for('login.login'))



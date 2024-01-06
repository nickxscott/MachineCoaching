from flask import Blueprint, render_template
from ..forms import *


login_bp = Blueprint('login', __name__, template_folder='../templates')

@login_bp.route('/')
def login():
	form = loginForm()
	return render_template('/login/login.html', form=form)

@login_bp.route('/test')
def test():
	return render_template('/login/test.html')
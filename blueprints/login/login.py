from flask import Blueprint, render_template

login_bp = Blueprint('login', __name__, template_folder='templates')

@login_bp.route('/')
def login():
	return render_template(login.html)

#imports
from flask import Flask, url_for
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

#custom imports
import config

#create app object
app = Flask(__name__, static_url_path='/static')
app.config.from_object(config)

#create login_manager  and bcrypt objects
login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = 'login.login' 
bcrypt = Bcrypt(app)

#import and register blueprints - do this after login_manager and bcrypt objects are created to avoid circular import error
from blueprints.login.login import login_bp
from blueprints.dashboard.dashboard import dashboard_bp
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)


if __name__ == '__main__':
	app.run(debug=True)
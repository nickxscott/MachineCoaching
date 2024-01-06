from flask import Flask
from blueprints.login.login import login_bp

import config

app = Flask(__name__, static_url_path='/static')
app.config.from_object(config)
app.register_blueprint(login_bp)


if __name__ == '__main__':
	app.run(debug=True)
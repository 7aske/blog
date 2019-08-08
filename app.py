from flask import Flask, render_template
from flask_cors import CORS
import routes
from datetime import datetime
from utils import setup_client

setup_client()
app = Flask(__name__)
cors = CORS(app)
app.register_blueprint(routes.index_route)
app.register_blueprint(routes.static_route)
app.register_blueprint(routes.creator_route)
app.register_blueprint(routes.login_route)
app.register_blueprint(routes.posts_route)
app.register_blueprint(routes.api_route)


@app.context_processor
def inject_year():
	return {'year': datetime.utcnow().strftime("%Y")}


@app.errorhandler(404)
def page_not_found(e):
	print(e)
	return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
	print(e)
	return render_template('500.html'), 500


if __name__ == "__main__":
	app.run(host="0.0.0.0")

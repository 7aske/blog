from flask import Flask, send_from_directory
from flask_cors import CORS
import routes
from utils import setup_client

setup_client()
app = Flask(__name__, static_url_path="/static", static_folder="client/build/static")
cors = CORS(app)

app.register_blueprint(routes.login_route)
app.register_blueprint(routes.api_route)
app.register_blueprint(routes.index_route)


@app.errorhandler(404)
def page_not_found(e):
	print(e)
	return send_from_directory("client/build", "index.html")


if __name__ == "__main__":
	app.run(host="0.0.0.0")

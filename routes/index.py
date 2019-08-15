from flask import request,  Blueprint, send_from_directory

index_route = Blueprint("index_route", __name__)


@index_route.route("/", methods=["GET"])
def routes_index():
	print(request.remote_addr)
	return send_from_directory("client/build", "index.html"), 200


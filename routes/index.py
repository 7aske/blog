from flask import request, render_template, Blueprint

index_route = Blueprint("index_route", __name__)


@index_route.route("/")
def routes_index():
	print(request.remote_addr)
	return render_template("index.html"), 200

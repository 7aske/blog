from flask import request, render_template, redirect, make_response, Blueprint

import auth
from config import config

ADMIN_USER = config.get("admin", "user", fallback="admin")
ADMIN_PASS = config.get("admin", "passwd", fallback="admin")
SECRET = config.get("admin", "secret", fallback="secret")

login_route = Blueprint("login_route", __name__)


@login_route.route("/login", methods=["GET", "POST"])
def routes_login():
	if request.method == "POST":
		username = request.form.get('admin_username')
		password = request.form.get('admin_passwd')

		if username != ADMIN_USER or auth.get_hash(ADMIN_PASS) != auth.get_hash(password):
			return render_template("login.html", errors=["Bad Credentials"])

		token = auth.generate_token()
		resp = make_response(redirect("/creator"))
		resp.set_cookie("authorization", "Bearer " + str(token, encoding="utf8"))
		return resp

	elif request.method == "GET":
		if auth.validate_request(request):
			return render_template("login.html"), 400

		return render_template("login.html"), 200
	else:
		return "Bad Request", 400

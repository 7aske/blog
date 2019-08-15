import json

from flask import request, render_template, redirect, make_response, Blueprint, Response

import auth
from config import config

ADMIN_USER = config.get("admin", "user", fallback="admin")
ADMIN_PASS = config.get("admin", "passwd", fallback="admin")
SECRET = config.get("admin", "secret", fallback="secret")

login_route = Blueprint("login_route", __name__)


@login_route.route("/validate", methods=["POST"])
def routes_validate():
	if auth.validate_request(request):
		return "Ok", 200
	return "Unauthorized", 401


@login_route.route("/login", methods=["GET", "POST"])
def routes_login():
	if request.method == "POST":
		if request.headers.get("TOKEN_ONLY", default="false") == "true":
			username = request.headers.get("Username")
			password = request.headers.get("Password")
			if username != ADMIN_USER or auth.get_hash(ADMIN_PASS) != auth.get_hash(password):
				return "Unauthorized", 401

			token = auth.generate_token()
			res = Response()
			res.headers.set("Content-Type", "application/json")
			res.set_data(json.dumps({"token": str(token, encoding="utf8")}))
			return res

		else:
			username = request.form.get('admin_username')
			password = request.form.get('admin_passwd')
			if username != ADMIN_USER or auth.get_hash(ADMIN_PASS) != auth.get_hash(password):
				return render_template("login.html", errors=["Bad Credentials"])

			token = auth.generate_token()
			res = make_response(redirect("/creator"))
			res.set_cookie("authorization", "Bearer " + str(token, encoding="utf8"))
			return res

	elif request.method == "GET":
		return render_template("login.html"), 200
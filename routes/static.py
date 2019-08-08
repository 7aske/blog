from flask import Blueprint, send_from_directory

static_route = Blueprint("static_route", __name__)


@static_route.route("/static/<path:p>", methods=["GET"])
def routes_static(p):
	return send_from_directory("static", p[8:]), 200


@static_route.route("/favicon.ico", methods=["GET"])
def route_favicon():
	return send_from_directory("static", "favicon.ico"), 200

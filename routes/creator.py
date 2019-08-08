import auth
from flask import Blueprint, request, render_template, redirect

creator_route = Blueprint("creator_route", __name__)


@creator_route.route("/creator", methods=["GET"])
def routes_creator():
	if auth.validate_request(request):
		return render_template("creator.html"), 200

	return redirect("/login")

from flask import render_template, Blueprint

from database import get_db

posts_route = Blueprint("posts_route", __name__)


@posts_route.route("/posts/<string:postid>", methods=["GET"])
def routes_posts(postid):
	p = get_db().db.posts.find_one_or_404({"id": postid})
	return render_template("post.html", post=p), 200

from flask import render_template, Blueprint

from database import get_db
from routes.api import postutils

posts_route = Blueprint("posts_route", __name__)


@posts_route.route("/posts/<string:postid>", methods=["GET"])
def routes_posts(postid):
	post = get_db().db.posts.find_one_or_404({"id": postid})
	return render_template("post.html", post=postutils.post_to_json(post)), 200

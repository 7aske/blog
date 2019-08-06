import pprint
from datetime import datetime
import json
from db import init_db, _cleanup
import atexit
import shortuuid

from flask import Flask, request, render_template, send_from_directory, Response
from flask_cors import CORS

TIME_FMT = "%d %B, %Y %H:%M:%S"

app = Flask(__name__)
cors = CORS(app)
mongo = init_db(app)


@app.route("/api/v1/posts", methods=["GET", "POST"])
def api_posts():
	if request.method == "POST":
		json_str = request.get_json()["data"]
		post = json.loads(json_str, encoding="utf8")
		print(post)
		if "body" in post.keys() and "title" in post.keys() and "category" in post.keys():
			post["date_posted"] = datetime.now()
			post["id"] = shortuuid.uuid()
			post["comments"] = []
			mongo.db.posts.insert(post)
			del post["_id"]
			post["date_posted"] = post["date_posted"].strftime(TIME_FMT)
		return json.dumps(post), 200
	elif request.method == "GET":
		res = {"posts": []}
		cursor = mongo.db.posts.find({})
		for p in cursor:
			del p["_id"]
			p["date_posted"] = p["date_posted"].strftime(TIME_FMT)
			for comment in p["comments"]:
				comment["date_posted"] = comment["date_posted"].strftime(TIME_FMT)
			res["posts"].append(p)
			pprint.pprint(p)
		resp = Response()
		resp.headers["Content-Type"] = "application/json"
		resp.set_data(json.dumps(res))
		return resp, 200


@app.route("/api/v1/posts/<string:postid>", methods=["GET"])
def api_post(postid):
	if request.method == "GET":
		print(postid)
		p = mongo.db.posts.find_one_or_404({"id": postid})
		if p is not None:
			del p["_id"]
			p["date_posted"] = p["date_posted"].strftime(TIME_FMT)
			for comment in p["comments"]:
				comment["date_posted"] = comment["date_posted"].strftime(TIME_FMT)
			pprint.pprint(p)
			return render_template("post.html", post=p)
		else:
			return None


@app.route("/api/v1/posts/<string:postid>/comments", methods=["GET", "POST"])
def api_post_comment(postid):
	if request.method == "POST":
		json_str = request.get_json()["data"]
		comment = json.loads(json_str, encoding="utf8")
		p = mongo.db.posts.find_one_or_404({"id": postid})
		if p is not None:
			comment["date_posted"] = datetime.now()
			comment["id"] = shortuuid.uuid()
			comment["votes"] = 0
			p["comments"].append(comment)
			mongo.db.posts.update_one({"id": postid}, {"$set": {"comments": p["comments"]}})
			return postid, 200

	return postid, 200


@app.route("/api/v1/posts/<string:postid>/comments/<string:commentid>", methods=["POST"])
def api_post_comment_vote(postid, commentid):
	delta = request.args.get("delta")
	if delta is not None:
		p = mongo.db.posts.find_one_or_404({"id": postid})

		if p is not None:
			pprint.pprint(p["comments"])
			print(delta)
			for comment in p["comments"]:
				if comment["id"] == commentid:
					if "votes" in comment.keys():
						comment["votes"] += int(delta)
					else:
						comment["votes"] = int(delta)
					pprint.pprint(p["comments"])
					mongo.db.posts.update_one({"id": postid}, {"$set": {"comments": p["comments"]}})
					comment["date_posted"] = comment["date_posted"].strftime(TIME_FMT)
					return json.dumps(comment)
	else:
		return "Invalid request", 405


@app.route("/posts/<string:postid>", methods=["GET"])
def routes_posts(postid):
	p = mongo.db.posts.find_one_or_404({"id": postid})
	if p is not None:
		del p["_id"]
		p["date_posted"] = p["date_posted"].strftime(TIME_FMT)
		for c in p["comments"]:
			c["date_posted"] = c["date_posted"].strftime(TIME_FMT)
		pprint.pprint(p)
		return render_template("post.html", post=p)
	else:
		return None


@app.route("/create", methods=["GET"])
def routes_create():
	return render_template("create.html")


@app.route("/static/<path:p>", methods=["GET"])
def routes_static(p):
	return send_from_directory("static", p[8:])


@app.route("/me/admin", methods=["GET"])
def routes_admin():
	return "ADMIN"


@app.route("/")
# index route
def routes_index():
	return render_template("index.html")


# def format_datetime(value, fmt="%x %X"):
# 	print(value)
# 	if value is None:
# 		return ""
# 	return datetime.strptime(value, "").strftime(fmt)
#
# app.jinja_env.filters['formatdatetime'] = format_datetime

@app.after_request
def add_header(r):
	r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	r.headers["Pragma"] = "no-cache"
	r.headers["Expires"] = "0"
	r.headers['Cache-Control'] = 'public, max-age=0'
	return r


@atexit.register
def cleanup():
	_cleanup()


if __name__ == "__main__":
	app.run(host="0.0.0.0")

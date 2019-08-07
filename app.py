from flask import Flask, request, render_template, send_from_directory, Response, make_response, redirect
from flask_cors import CORS
import jwt
import configparser

import pprint
from datetime import datetime, timedelta
import json
import atexit
import shortuuid

from db import init_db, _cleanup
from utils import get_hash

TIME_FMT = "%d %B, %Y %H:%M:%S"

cfparser = configparser.ConfigParser()

cfparser.read("configs/admin.conf")

ADMIN_USER = cfparser["credentials"]["user"]
ADMIN_PASS = cfparser["credentials"]["passwd"]

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
			return json.dumps(post), 201
		else:
			return "Bad Request", 400
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
	else:
		return "Bad Request", 400


@app.route("/api/v1/posts/<string:postid>", methods=["GET", "POST"])
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
			return render_template("post.html", post=p), 200
		else:
			return "Not Found", 404
	elif request.method == "POST":
		delta = request.args.get("delta")
		if delta is not None:
			vote_point = int(delta)
			p = mongo.db.posts.find_one_or_404({"id": postid})
			if p is not None:

				h = get_hash(request.remote_addr)
				voter = mongo.db.voters.find_one({"voter": h})
				if not voter:
					print(h)
					print("not found")
					mongo.db.voters.insert({"voter": h, "votes": []})
				else:
					for vote in voter["votes"]:
						if vote["id"] == postid:
							if vote["vote"] < 0 and vote_point < 0 or vote["vote"] > 0 and vote_point > 0:
								print("already voted")
								return "Bad Request", 400
							else:
								voter["votes"].remove(vote)
					voter["votes"].append({"id": postid, "vote": vote_point, "date_voted": str(datetime.now())})
					mongo.db.voters.update_one({"voter": h}, {"$set": {"votes": voter["votes"]}})

				if "votes" in p.keys():
					p["votes"] += vote_point
				else:
					p["votes"] = vote_point
				mongo.db.posts.update_one({"id": postid}, {"$set": {"votes": p["votes"]}})
				p["date_posted"] = p["date_posted"].strftime(TIME_FMT)
				del p["comments"]
				del p["_id"]
				return json.dumps(p), 201
			else:
				return "Not Found", 404
		else:
			return "Bad Request", 400
	else:
		return "Bad Request", 400


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
			return postid, 201
		else:
			return "Not Found", 404
	elif request.method == "GET":
		p = mongo.db.posts.find_one_or_404({"id": postid})
		if p is not None:
			for comment in p["comments"]:
				comment["date_posted"] = comment["date_posted"].strftime(TIME_FMT)

			return json.dumps({"comments": p["comments"]}), 200
		else:
			return "Not Found", 404
	else:
		return "Bad Request", 400


@app.route("/api/v1/posts/<string:postid>/comments/<string:commentid>", methods=["POST"])
def api_post_comment_vote(postid, commentid):
	delta = request.args.get("delta")
	if delta is not None:
		p = mongo.db.posts.find_one_or_404({"id": postid})
		if p is not None:
			vote_point = int(delta)
			for comment in p["comments"]:
				if comment["id"] == commentid:
					h = get_hash(request.remote_addr)
					voter = mongo.db.voters.find_one({"voter": h})
					if not voter:
						mongo.db.voters.insert({"voter": h, "votes": []})
					else:
						for vote in voter["votes"]:
							if vote["id"] == commentid:
								if vote["vote"] < 0 and vote_point < 0 or vote["vote"] > 0 and vote_point > 0:
									print("already voted")
									return "Bad Request", 400
								else:
									voter["votes"].remove(vote)
						voter["votes"].append({"id": commentid, "vote": vote_point, "date_voted": str(datetime.now())})
						mongo.db.voters.update_one({"voter": h}, {"$set": {"votes": voter["votes"]}})
					if "votes" in comment.keys():
						comment["votes"] += vote_point
					else:
						comment["votes"] = vote_point
					pprint.pprint(p["comments"])
					mongo.db.posts.update_one({"id": postid}, {"$set": {"comments": p["comments"]}})
					comment["date_posted"] = comment["date_posted"].strftime(TIME_FMT)
					return json.dumps(comment), 201
				else:
					return "Not Found", 404
		else:
			return "Not Found", 404
	else:
		return "Bad Request", 400


@app.route("/posts/<string:postid>", methods=["GET"])
def routes_posts(postid):
	p = mongo.db.posts.find_one_or_404({"id": postid})
	if p is not None:
		del p["_id"]
		p["date_posted"] = p["date_posted"].strftime(TIME_FMT)
		for c in p["comments"]:
			c["date_posted"] = c["date_posted"].strftime(TIME_FMT)
		pprint.pprint(p)
		return render_template("post.html", post=p), 200
	else:
		return "Not Found", 404


@app.route("/create", methods=["GET"])
def routes_create():
	cookie = request.cookies.get("authorization", None)
	if cookie:
		parts = cookie.split(" ")
		if len(parts) == 2:
			if parts[0] == "Bearer":
				try:
					token = jwt.decode(parts[1], "secret",
					                     algorithm="HS256")
					print(token)
					return render_template("create.html"), 200
				except (jwt.DecodeError, jwt.ExpiredSignatureError):
					return redirect("/login")

	return redirect("/login")


@app.route("/static/<path:p>", methods=["GET"])
def routes_static(p):
	return send_from_directory("static", p[8:]), 200


@app.route("/login", methods=["GET", "POST"])
def routes_login():
	if request.method == "POST":
		username = request.form.get('admin_username')
		password = request.form.get('admin_passwd')
		print(username, password)

		if username != ADMIN_USER or get_hash(ADMIN_PASS) != get_hash(password):
			return render_template("login.html", errors=["Bad Credentials"])

		token = jwt.encode({'issuedAt': str(datetime.now()), "expiresAt": str(datetime.now() + timedelta(hours=3))},
		                   'secret', algorithm='HS256')
		print(token)
		resp = make_response(redirect("/create"))
		resp.set_cookie("authorization", "Bearer " + str(token, encoding="utf8"))
		return resp
	elif request.method == "GET":
		header = request.headers.get("authrorization", None)
		if header:
			parts = header.split(" ")
			if len(parts) == 2:
				if parts[0] == "Bearer":
					try:
						token = jwt.decode(parts[1], "secret",
						                     algorithm="HS256")
						print(token)
						return redirect("/create")
					except (jwt.DecodeError, jwt.ExpiredSignatureError):
						return render_template("login.html"), 400

		return render_template("login.html"), 200
	else:
		return "Bad Request", 400


@app.route("/")
# index route
def routes_index():
	print(request.remote_addr)
	return render_template("index.html"), 200


@app.context_processor
def inject_year():
	return {'year': datetime.utcnow().strftime("%Y")}


@app.errorhandler(404)
def page_not_found(e):
	print(e)
	return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
	print(e)
	return render_template('500.html'), 500


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

from datetime import datetime
import json
from flask import Blueprint, request, Response
import flask_pymongo
import asyncio

import auth
import utils
import routes.api.postutils as postutils
from config import config
from database import get_db
from routes.api import commentutils

TIME_FMT = config.get("DEFAULT", "TIME_FORMAT", fallback="%d %B, %Y %H:%M:%S")
api_route = Blueprint("api_route", __name__)


@api_route.route("/api/v1/posts", methods=["GET", "POST"])
def api_posts():
	if request.method == "POST":
		if auth.validate_request(request):
			post = postutils.request_to_post(request)
			if post is not None:
				get_db().db.posts.insert(post)
				return json.dumps(postutils.post_to_json(post)), 201
		else:
			return "Unauthorized", 401

		return "Bad Request", 400
	elif request.method == "GET":
		start = int(request.args.get("start", default=0))
		count = int(request.args.get("count", default=5))
		res = {"posts": []}
		cursor = get_db().db.posts.find({}).sort([("_id", flask_pymongo.DESCENDING)]).limit(count - start).skip(start)
		for post in cursor:
			p = postutils.post_to_json(post)
			res["posts"].append(p)
		resp = Response()
		resp.headers["Content-Type"] = "application/json"
		resp.set_data(json.dumps(res))
		return resp, 200
	else:
		return "Bad Request", 400


@api_route.route("/api/v1/posts/<string:postid>", methods=["GET", "POST", "PUT", "DELETE"])
def api_post(postid):
	if request.method == "GET":
		post = get_db().db.posts.find_one_or_404({"id": postid})
		if post is not None:
			post = postutils.post_to_json(post)
			res = Response()
			res.set_data(json.dumps({"post": post}, default=lambda o: str(o)))
			return res, 200
		else:
			return "Not Found", 404
	elif request.method == "POST":
		delta = request.args.get("delta")
		addr = request.headers.get("X-Forwarded-For", default=request.remote_addr)
		if delta is not None:
			vote_point = int(delta)
			post = get_db().db.posts.find_one_or_404({"id": postid})
			addr_hash = utils.get_hash(addr)
			voter = get_db().db.voters.find_one({"voter": addr_hash})
			if not voter:
				voter = {"voter": addr_hash, "votes": [
					{"id": postid, "delta": vote_point, "date_voted": str(datetime.now())}]}
				get_db().db.voters.insert(voter)
				post["votes"] += vote_point
			else:
				post["votes"] += postutils.add_vote_point(voter, postid, vote_point)
				get_db().db.voters.update_one({"voter": voter["voter"]}, {"$set": {"votes": voter["votes"]}})

			get_db().db.posts.update_one({"id": postid}, {"$set": {"votes": post["votes"]}})
			ret = postutils.post_to_json(post)
			del ret["comments"]
			return json.dumps(ret), 201
		else:
			return "Bad Request", 400
	elif request.method == "PUT":
		if auth.validate_request(request):
			updated_post = postutils.request_to_post(request)
			post = get_db().db.posts.find_one_or_404({"id": postid})
			if post is not None:
				get_db().db.posts.update_one({"id": post["id"]}, {
					"$set": {"body"    : updated_post["body"], "description": updated_post["description"],
					         "category": updated_post["category"], "title": updated_post["title"]}})
				return json.dumps(postutils.post_to_json(updated_post)), 201
		else:
			return "Unauthorized", 401
	elif request.method == "DELETE":
		if auth.validate_request(request):
			deleted = get_db().db.posts.delete_one({"id": postid})
			if deleted.deleted_count > 0:
				return json.dumps({"deleted": deleted.deleted_count}), 200
			else:
				return "Not Found", 404
		else:
			return "Unauthorized", 401
	return "Bad Request", 400


@api_route.route("/api/v1/posts/<string:postid>/comments", methods=["GET", "POST"])
def api_post_comment(postid):
	if request.method == "POST":
		comment = commentutils.request_to_comment(request)
		if comment is not None:
			post = get_db().db.posts.find_one_or_404({"id": postid})
			post["comments"].append(comment)
			if "mailer" in config.sections():
				commentutils.mail_commenters(post, comment)
			get_db().db.posts.update_one({"id": postid}, {"$set": {"comments": post["comments"]}})
			return json.dumps(commentutils.comment_to_json(comment)), 201
		else:
			return "Not Found", 404
	elif request.method == "GET":
		post = get_db().db.posts.find_one_or_404({"id": postid})
		addr = request.headers.get("X-Forwarded-For", default=request.remote_addr)
		voter = get_db().db.voters.find_one({"voter", utils.get_hash(addr)})
		for comment in post["comments"]:
			comment["date_posted"] = comment["date_posted"].strftime(TIME_FMT)
		res = Response()
		res.set_data(json.dumps({"voter": voter, "comments": post["comments"]}, default=lambda o: str(o)))
		return res, 200
	else:
		return "Bad Request", 400


@api_route.route("/api/v1/posts/<string:postid>/comments/<string:commentid>", methods=["POST"])
def api_post_comment_vote(postid, commentid):
	delta = request.args.get("delta")
	addr = request.headers.get("X-Forwarded-For", default=request.remote_addr)
	print(delta)
	if delta is not None:
		post = get_db().db.posts.find_one_or_404({"id": postid})
		vote_point = int(delta)
		print(post["comments"])
		for comment in post["comments"]:
			print(comment["id"], commentid)
			if comment["id"] == commentid:
				addr_hash = utils.get_hash(addr)
				voter = get_db().db.voters.find_one({"voter": addr_hash})
				if not voter:
					voter = {"voter": addr_hash, "votes": [
						{"id": commentid, "delta": vote_point, "date_voted": str(datetime.now())}]}
					get_db().db.voters.insert(voter)
					comment["votes"] += vote_point
				else:
					comment["votes"] += postutils.add_vote_point(voter, commentid, vote_point)
					get_db().db.voters.update_one({"voter": addr_hash}, {"$set": {"votes": voter["votes"]}})

				get_db().db.posts.update_one({"id": postid}, {"$set": {"comments": post["comments"]}})
				return json.dumps(commentutils.comment_to_json(comment)), 201
		else:
			return "Not Found", 404
	else:
		return "Bad Request", 400


@api_route.route("/api/v1/voters/<string:oid>", methods=["GET"])
def api_get_voters(oid):
	if request.method == "GET":
		addr = request.headers.get("X-Forwarded-For", default=request.remote_addr)
		voter = get_db().db.voters.find_one({"voter": utils.get_hash(addr)})
		post = get_db().db.posts.find_one({"id": oid})
		if voter:
			voter["votes"] = [vote for vote in voter["votes"] if vote["id"] == oid or vote["id"] in [comment["id"] for
			                                                                                         comment in
			                                                                                         post["comments"]]]
			res = Response()
			res.set_data(json.dumps({"voter": voter}, default=lambda o: str(o)))
			return res, 200

	return "Not Found", 404

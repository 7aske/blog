from datetime import datetime
import json

import flask
import shortuuid

from config import config

TIME_FMT = config.get("DEFAULT", "TIME_FORMAT", fallback="%d %B, %Y %H:%M:%S")


def post_to_json(post):
	if "_id" in post.keys():
		del post["_id"]
	post["date_posted"] = post["date_posted"].strftime(TIME_FMT)
	for comment in post["comments"]:
		comment["date_posted"] = comment["date_posted"].strftime(TIME_FMT)
	return post


def request_to_post(request: flask.Request):
	try:
		json_str = request.get_json()["data"]
		post_json = json.loads(json_str, encoding="utf8")
	except Exception as e:
		print(e)
		return None
	if "body" in post_json.keys() and "title" in post_json.keys() and "category" in post_json.keys():
		return {
			"body"       : post_json["body"],
			"title"      : post_json["title"],
			"category"   : post_json["category"],
			"description": post_json["description"],
			"date_posted": datetime.now(),
			"id"         : shortuuid.uuid(),
			"votes"      : 0,
			"comments"   : [],
		}
	return None


def add_vote_point(voter, postid, vote_point):
	if postid not in [vote["id"] for vote in voter["votes"]]:
		if vote_point < -1:
			vote_point = -1
		elif vote_point < 1:
			vote_point = 1
		newvote = {"id": postid, "delta": vote_point, "date_voted": str(datetime.now())}
		voter["votes"].append(newvote)
		return vote_point

	for vote in voter["votes"]:
		if vote["id"] == postid:
			if vote_point < 0:
				if vote["delta"] + vote_point >= -1:
					vote["delta"] += vote_point
					return vote_point
			elif vote_point > 0:
				if vote["delta"] + vote_point <= 1:
					vote["delta"] += vote_point
					return vote_point
	return 0

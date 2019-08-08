from datetime import datetime
import flask
import json
import shortuuid
from config import config

TIME_FMT = config.get("DEFAULT", "TIME_FORMAT", fallback="%d %B, %Y %H:%M:%S")


def request_to_comment(request: flask.Request):
	try:
		json_str = request.get_json()["data"]
		comment_json = json.loads(json_str, encoding="utf8")
	except Exception as e:
		print(e)
		return None

	if "author" in comment_json.keys() and "email" in comment_json.keys() and "text" in comment_json.keys():
		return {
			"author"     : comment_json["author"],
			"email"      : comment_json["email"],
			"text"       : comment_json["text"],
			"date_posted": datetime.now(),
			"id"         : shortuuid.uuid(),
			"votes"      : 0,
		}
	return None


def comment_to_json(comment):
	comment["date_posted"] = comment["date_posted"].strftime(TIME_FMT)
	return comment

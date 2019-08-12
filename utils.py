import socket
import random
import subprocess
import sys
from os import path, getenv
from config import config


def get_random_port(prange: tuple) -> int:
	if getenv("FLASK_ENV", None) == "development":
		return 27017
	port = random.randint(prange[0], prange[1])
	while not is_port_open(port):
		port = random.randint(prange[0], prange[1])
	return port


def setup_client():
	if not path.exists("static/node_modules"):
		npm = subprocess.Popen(["npm", "-C", path.join(path.dirname(__file__), "static"), "install"], stdout=sys.stderr)
		npm.wait()


def is_port_open(port: int) -> bool:
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		result = sock.connect_ex(('127.0.0.1', port))
		print(port, result)
		if result == 0:
			sock.close()
			return False
		else:
			sock.close()
			return True
	except Exception as e:
		print(e)
		sys.exit(1)


def format_post_output(post: dict):
	del post["_id"]
	post["date_posted"] = post["date_posted"].strftime(config["DEFAULT"]["TIME_FMT"])
	for comment in post["comments"]:
		comment["date_posted"] = comment["date_posted"].strftime(config["DEFAULT"]["TIME_FMT"])


def get_hash(obj: object) -> str:
	import hashlib
	m = hashlib.sha256()
	m.update(bytes(obj, "utf8"))
	return m.hexdigest()

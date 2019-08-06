import subprocess
from utils import get_random_port
from flask_pymongo import PyMongo
from os import path, mkdir
from time import sleep
import sys
import signal

PORT_RANGE = (30000, 50000)

DB_CONF_PATH = path.join(path.dirname(__file__), "configs/db.yaml")
DB_PATH = path.join(path.dirname(__file__), "db")
DB_NAME = "admin"
DB_USER = "admin"
DB_PASS = "admin"

_DB_PROC = None



def get_mongo_uri(db, user, pwd, port):
	return f"mongodb://{user}:{pwd}@127.0.0.1:{port}/{db}"


def init_db(app):
	global _DB_PROC
	port = get_random_port(PORT_RANGE)
	app.config["DB_PORT"] = port
	app.config["MONGO_URI"] = get_mongo_uri(DB_NAME, DB_USER, DB_PASS, port)
	try:
		_DB_PROC = _start_mongod(port)
	except Exception as e:
		print(e)
		sys.exit(1)

	mongo = PyMongo(app)
	return mongo


def _start_mongod(port):
	global _DB_PROC
	if _DB_PROC is None:
		if not path.exists(DB_PATH):
			mkdir(DB_PATH)
			_init_root_user(DB_NAME, DB_USER, DB_PASS, port)
		proc = subprocess.Popen(
			["mongod", "--auth", f"--dbpath={DB_PATH}", f"--config={DB_CONF_PATH}", f"--port={port}"])
		sleep(1)
		sys.stderr.write(f"INFO mongod server running on port {port}\n")
		return proc
	return None


def _init_root_user(database: str, username: str, password: str, port: int):
	# 'sleep(1)' is there to ensure that the previous command has been executed
	swtich_db_cmd = f"use {database}\n"
	create_user_cmd = "db.createUser({user: \"%s\", pwd: \"%s\", roles: [\"root\"]})\n" % (username, password)
	collection = "posts"
	create_collection_cmd = "db.createCollection(\"%s\")\n" % collection
	# start mongod without '--auth' flag
	md = subprocess.Popen(
		["mongod", f"--dbpath={DB_PATH}", f"--config={DB_CONF_PATH}", f"--port={port}"])
	sleep(1)
	# connect to mongodb to create a user
	m = subprocess.Popen(["mongo", "--port", str(port)], stdin=subprocess.PIPE, stdout=sys.stderr)
	# write commands to stdin of the client
	sys.stderr.write("INFO cmd: " + swtich_db_cmd)
	m.stdin.write(bytes(swtich_db_cmd, encoding="utf8"))
	sys.stderr.write("INFO cmd: " + create_user_cmd)
	m.stdin.write(bytes(create_user_cmd, encoding="utf8"))
	sys.stderr.write("INFO cmd: " + create_collection_cmd)
	m.stdin.write(bytes(create_collection_cmd, encoding="utf8"))
	sys.stderr.write("MONGO CLIENT:" + str(m.communicate()) + "\n")
	m.stdin.close()
	sleep(1)
	# send 'SIGINT' to both client and server
	m.send_signal(signal.SIGINT)
	md.send_signal(signal.SIGINT)
	sleep(1)


def _cleanup():
	global _DB_PROC
	if _DB_PROC is not None:
		_DB_PROC.send_signal(signal.SIGINT)
		_DB_PROC = None

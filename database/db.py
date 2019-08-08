import atexit
import subprocess
from utils import get_random_port
from flask_pymongo import PyMongo
from os import path, mkdir, getcwd
from time import sleep
import sys
import signal
from flask import current_app
from config import config

_PORT_RANGE = (30000, 50000)

DB_CONF_PATH = path.join(getcwd(), "configs/db.yaml")
DB_PATH = path.join(getcwd(), "db")
DB_PORT = 0
DB_NAME = config.get("db", "name", fallback="admin")
DB_USER = config.get("db", "user", fallback="admin")
DB_PASS = config.get("db", "passwd", fallback="admin")
_MONGO = None
_DB_PROC = None


def get_mongo_uri(db: str, user: str, pwd: str, port: int = 27017, host: str = "127.0.0.1"):
	return f"mongodb://{user}:{pwd}@{host}:{port}/{db}"


def get_db():
	if _MONGO is None:
		init_db()
	return _MONGO


def init_db():
	global _DB_PROC, DB_PORT, _MONGO
	if DB_PORT == 0:
		DB_PORT = get_random_port(_PORT_RANGE)
	current_app.config["DB_PORT"] = DB_PORT
	current_app.config["MONGO_URI"] = get_mongo_uri(DB_NAME, DB_USER, DB_PASS, DB_PORT)
	try:
		_DB_PROC = _start_mongod()
	except Exception as e:
		print(e)
		sys.exit(1)
	_MONGO = PyMongo(current_app)
	return _MONGO


def _start_mongod():
	global _DB_PROC
	if _DB_PROC is not None:
		return _DB_PROC

	if not path.exists(DB_PATH):
		mkdir(DB_PATH)
		_init_root_user(DB_NAME, DB_USER, DB_PASS, DB_PORT, DB_NAME)
	proc = subprocess.Popen(
		["mongod", "--auth", f"--dbpath={DB_PATH}", f"--config={DB_CONF_PATH}", f"--port={DB_PORT}"],
		stdout=sys.stderr)
	sleep(1)
	if proc.returncode is None:
		sys.stderr.write(f"INFO mongod server running on port {DB_PORT}\n")
	else:
		sys.stderr.write(f"INFO mongod exit code '{proc.returncode}'\n")
	return proc


def _init_root_user(database: str, username: str, password: str, port: int, dbname: str):
	# 'sleep(1)' is there to ensure that the previous command has been executed
	swtich_db_cmd = f"use {database}\n"
	create_user_cmd = "db.createUser({user: \"%s\", pwd: \"%s\", roles: [{role: \"root\", db: \"%s\"}]})\n" % (username, password, dbname)
	collection = "posts"
	create_collection_cmd = "db.createCollection(\"%s\")\n" % collection
	# start mongod without '--auth' flag
	md = subprocess.Popen(
		["mongod", f"--dbpath={DB_PATH}", f"--config={DB_CONF_PATH}", f"--port={port}"], stdout=sys.stderr)
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
	m.stdin.close()
	sleep(1)
	# send 'SIGINT' to both client and server
	m.send_signal(signal.SIGINT)
	md.send_signal(signal.SIGINT)
	m.wait()
	md.wait()


@atexit.register
def app_cleanup():
	_cleanup()


def _cleanup():
	global _DB_PROC
	if _DB_PROC is not None:
		_DB_PROC.send_signal(signal.SIGINT)
		_DB_PROC = None

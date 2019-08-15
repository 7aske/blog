import hashlib

import jwt
import time
from config import config


def validate_token(token: str) -> (bool, dict):
	if token is None:
		return False
	try:
		token = jwt.decode(token, config["admin"]["secret"], algorithm="HS256")
		return True, token
	except (jwt.DecodeError, jwt.ExpiredSignatureError) as e:
		print(e)
		return False


def validate_request(request) -> (bool, dict):
	cookie = request.cookies.get("authorization", None)
	if cookie:
		cookie = cookie.replace("Bearer%20", "Bearer ")
		parts = cookie.split(" ")
		if len(parts) == 2 and parts[0] == "Bearer":
			return validate_token(parts[1])
	else:
		token = request.headers.get("Token")
		if token:
			if validate_token(token):
				return "Ok", 200
	return False


def generate_token() -> bytes:
	now = time.time()
	exp = now + timeconv(hours=3)
	print(now, exp)
	payload = {'iat': int(now), "exp": int(exp)}
	return jwt.encode(payload, config["admin"]["secret"], algorithm='HS256')


def timeconv(seconds=0, minutes=0, hours=0, days=0):
	return seconds + minutes * 60 + hours * 60 * 60 + days * 60 * 60 * 24


def get_hash(obj) -> str:
	m = hashlib.sha256()
	m.update(bytes(obj, "utf8"))
	return m.hexdigest()

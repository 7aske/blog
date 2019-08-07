import socket
import random
import sys
import hashlib


def get_random_port(range: tuple) -> int:
	port = random.randint(range[0], range[1])
	while not is_port_open(port):
		port = random.randint(range[0], range[1])
	return port


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


def get_hash(obj):
	m = hashlib.sha256()
	m.update(bytes(obj, "utf8"))
	return m.hexdigest()

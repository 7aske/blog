import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import config


class Mailer:
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.server = smtplib.SMTP('smtp.gmail.com', 587)

	def __enter__(self):
		self.server.starttls()
		self.server.login(self.username, self.password)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.server:
			self.server.quit()

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import config
from services.mailer import Mailer
import os


class CommentMailer(Mailer):
	def send_mail(self, user, title, comment, postid, mail_to):
		href = "http://" + config.get("host", "name") + ":" + os.getenv("FLASK_RUN_PORT") + "/posts/" + postid
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Post comment"
		msg['From'] = self.username
		msg['To'] = mail_to
		html = "<html><head><style>* {{font-family: 'Consolas', 'Deja Vu Sans Mono', 'Bitstream Vera Sans Mono', monospace}}</style></head><body>{user} has also commented in '<a target=\"_blank\" href=\"{href}\"><b>{title}</b></a>'.<br><br>\"{comment}\"</body></html>".format(
			user=user, title=title, comment=comment, href=href)
		text = "{user} has also commented in '{title}'.\n\n\"{comment}\"".format(user=user, title=title,
		                                                                         comment=comment)
		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(html, 'html')
		msg.attach(part1)
		msg.attach(part2)
		try:
			self.server.sendmail(self.username, mail_to, msg.as_string())
		except Exception as e:
			print(str(e))

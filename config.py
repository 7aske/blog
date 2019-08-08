import configparser

config = configparser.ConfigParser()

config.read("configs/admin.conf")
config.set("DEFAULT", "TIME_FORMAT", "%%d %%B, %%Y %%H:%%M:%%S")

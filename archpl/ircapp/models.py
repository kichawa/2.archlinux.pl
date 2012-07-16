from django.db import models


class Configuration(models.Model):
    server_port = models.IntegerField(default=6667)
    server_host = models.CharField(max_length=32, default='irc.freenode.net')
    realname = models.CharField(max_length=16, default='IRC app bot')
    nickname = models.CharField(max_length=9, default='ircappbot')
    channel = models.CharField(max_length=50)

    def server_address(self):
        return "{}:{}".format(self.server_host, self.server_port)


class Message(models.Model):
    has_url = models.BooleanField(default=False)
    has_img = models.BooleanField(default=False)
    message = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    channel = models.CharField(max_length=50)
    protocol = models.CharField(max_length=10)
    author = models.CharField(max_length=9)

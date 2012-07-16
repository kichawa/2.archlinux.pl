import irc.bot

from models import Configuration, Message




class Bot(irc.bot.SingleServerIRCBot):
    @classmethod
    def from_db_configuration(cls):
        confs = list(Configuration.objects.all())
        if not confs:
            return None
        server_list = []

        addr = confs[0].server_address()
        for c in confs:
            if c.server_addr() != addr:
                raise Exception("Multiple servers connection not supported")
            server_list.append((c.server_host, c.server_port))
        return cls(server_list=server_list)

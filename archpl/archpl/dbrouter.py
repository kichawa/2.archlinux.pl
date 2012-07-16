class DBRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ircapp':
            return 'irc'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ircapp':
            return 'irc'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        lab1 = obj1._meta.app_label
        lab2 = obj2._meta.app_label
        if lab1 == lab2:
            return True
        return 'ircapp' not in [lab1, lab2]

    def allow_syncdb(self, db, model):
        if db == 'irc':
            return model._meta.app_label == 'ircapp'
        return model._meta.app_label != 'ircapp'

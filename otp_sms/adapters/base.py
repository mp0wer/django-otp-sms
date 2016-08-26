# -*- coding: utf-8 -*-


class BaseAdapter(object):
    def __init__(self, auth):
        self.auth = auth

    def send(self, number, message, **kwargs):
        raise NotImplementedError


class ConsoleAdapter(BaseAdapter):
    def send(self, number, message, **kwargs):
        print
        print 'Sent to %s message "%s"' % (number, message)
        print


class AdapterError(Exception):
    pass